"""Experiment A: COFOG budget-composition forecasting (real Eurostat/OECD targets, 16 sectors + residual).

A1  temporal one-step-ahead with history   (train <=2019, test 2020-2024; lag shares available)
A2  cold-start, leave-country-out CV       (6-fold grouped by country, 2 fold-seeds; no lag information)
A3  ablation of feature groups (cold-start, XGBoost)
Outputs: results/02_main_experiments/*.csv|json
"""
import json, sys
import numpy as np, pandas as pd
from sklearn.model_selection import GroupKFold
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from gov_common import *

d = load_cofog()
T = TARGETS_A
LAG = [f"lag_{t}" for t in T]
print("panel", d.shape, "countries", d.iso3.nunique(), "rows with lag", int(d.has_lag.sum()))
lo_q, hi_q = 0.01, 0.99


def bounds(Y):
    """Default policy bounds: 0.5 x historical minimum .. 1.5 x historical maximum (see bounds-sensitivity table)."""
    return Y.min().values * 0.5, Y.max().values * 1.5


def score(P, A, groups, label, extra=None):
    P = simplex_renorm(np.asarray(P)); A = np.asarray(A)
    t = tvd(P, A)
    lo, hi = boot_ci(t, groups)
    r = {"method": label, "TVD": float(t.mean()), "TVD_lo": lo, "TVD_hi": hi, "MAE_pp": float(np.abs(P - A).mean()),
         "RMSE_pp": float(np.sqrt(((P - A) ** 2).mean())), "n": int(len(A))}
    sect_mae = np.abs(P - A).mean(0)
    r.update({f"mae_{c.replace('cofog_','').replace('_pct_total','')}": float(v) for c, v in zip(T, sect_mae)})
    if extra: r.update(extra)
    return r, t


# ---------------------------------------------------------------- A1 temporal with history
tr = d[(d.year <= 2019) & d.has_lag]; te = d[(d.year >= 2020) & d.has_lag]
print("A1 train", len(tr), "test", len(te), "test countries", te.iso3.nunique())
Ytr, Yte = tr[T], te[T]
rows, tv = [], {}
r, t = score(te[LAG].values, Yte, te.iso3, "Persistence (last year)"); rows.append(r); tv[r["method"]] = t
cm = tr.groupby("iso3")[T].mean(); gm = tr[T].mean()
P = np.vstack([cm.loc[i].values if i in cm.index else gm.values for i in te.iso3])
r, t = score(P, Yte, te.iso3, "Country mean (train)"); rows.append(r); tv[r["method"]] = t
Xtr, Xte = tr[FEATURES], te[FEATURES]
Xtr_l, Xte_l = tr[FEATURES + LAG], te[FEATURES + LAG]
for m in ["ridge", "rf", "xgb", "lgbm", "cat"]:
    P = fit_predict_multi(m, Xtr, Ytr, Xte)
    r, t = score(P.values, Yte, te.iso3, f"ML features-only: {m}"); rows.append(r); tv[r["method"]] = t
dp = {}
Dtr = Ytr.values - tr[LAG].values
Dtr = pd.DataFrame(Dtr, columns=T, index=tr.index)
for m in ["ridge", "rf", "xgb", "lgbm", "cat"]:
    D = fit_predict_multi(m, Xtr_l, Dtr, Xte_l)
    dp[m] = D
    r, t = score(te[LAG].values + D.values, Yte, te.iso3, f"Delta-ML (lag + learned change): {m}"); rows.append(r); tv[r["method"]] = t
Dh = 0.5 * dp["xgb"] + 0.5 * dp["cat"]
r, t = score(te[LAG].values + Dh.values, Yte, te.iso3, "Delta-ML Hybrid (50% XGB + 50% CatBoost)"); rows.append(r); tv[r["method"]] = t
A1 = pd.DataFrame(rows); A1.to_csv(RES / "02_main_experiments/temporal_history.csv", index=False)
print(A1[["method", "TVD", "TVD_lo", "TVD_hi", "MAE_pp"]].round(3).to_string())

# paired comparison: hybrid delta vs persistence (cluster bootstrap on country means of paired TVD difference)
diff = tv["Persistence (last year)"] - tv["Delta-ML Hybrid (50% XGB + 50% CatBoost)"]
dlo, dhi = boot_ci(diff, te.iso3.values)
A1_paired = {"mean_TVD_reduction_vs_persistence": float(diff.mean()), "ci95": [dlo, dhi],
             "share_of_rows_improved": float((diff > 0).mean())}
print("paired", A1_paired)

# change-prediction ability (does the model anticipate shifts?)
dact = (Yte.values - te[LAG].values); dprd = Dh.values
dyn = []
for j, c in enumerate(T):
    a, p = dact[:, j], dprd[:, j]
    dyn.append({"sector": c.replace("cofog_", "").replace("_pct_total", ""), "corr_delta": float(np.corrcoef(a, p)[0, 1]) if a.std() > 0 else np.nan,
                "dir_acc": float((np.sign(a[np.abs(a) > 0.05]) == np.sign(p[np.abs(a) > 0.05])).mean()), "mean_abs_actual_delta": float(np.abs(a).mean())})
pd.DataFrame(dyn).to_csv(RES / "02_main_experiments/delta_dynamics.csv", index=False)
# covid-specific check: 2020 health & social protection change
c20 = te.year == 2020
cov = {}
for s in ["health", "social_protection", "education", "defence"]:
    j = T.index(f"cofog_{s}_pct_total")
    cov[s] = {"actual_mean_delta_2020": float(dact[c20.values, j].mean()), "pred_mean_delta_2020": float(dprd[c20.values, j].mean()),
              "corr_2020": float(np.corrcoef(dact[c20.values, j], dprd[c20.values, j])[0, 1])}
print("covid", cov)
# constrained allocation engine on the best temporal model
Pbest = simplex_renorm(te[LAG].values + Dh.values)
lo, hi = bounds(Ytr)
Pal = allocate(Pbest, lo, hi)
pd.DataFrame({"iso3": te.iso3.values, "year": te.year.values, **{f"pred_{c}": Pbest[:, j] for j, c in enumerate(T)},
              **{f"alloc_{c}": Pal[:, j] for j, c in enumerate(T)}, **{f"act_{c}": Yte.values[:, j] for j, c in enumerate(T)}}
             ).to_csv(RES / "02_main_experiments/best_predictions.csv", index=False)
eng = {"TVD_before_constraints": float(tvd(Pbest, Yte.values).mean()), "TVD_after_constraints": float(tvd(Pal, Yte.values).mean()),
       "rows_violating_bounds_before": float(((Pbest < lo - 1e-9) | (Pbest > hi + 1e-9)).any(1).mean()),
       "max_sum_error_after": float(np.abs(Pal.sum(1) - 100).max())}
# bound-width sensitivity of the allocation engine
sens = []
for name, (l_, h_) in {"1st-99th pctile": (Ytr.quantile(.01).values, Ytr.quantile(.99).values),
                        "min-max (train)": (Ytr.min().values, Ytr.max().values),
                        "0.5xmin - 1.5xmax": (Ytr.min().values * .5, Ytr.max().values * 1.5),
                        "none (renorm only)": (np.zeros(len(T)), np.full(len(T), 100.0))}.items():
    Pq = allocate(Pbest, l_, h_)
    sens.append({"bounds": name, "TVD": float(tvd(Pq, Yte.values).mean()), "rows_pred_outside_bounds": float(((Pbest < l_ - 1e-9) | (Pbest > h_ + 1e-9)).any(1).mean()),
                 "actual_rows_outside_bounds": float(((Yte.values < l_ - 1e-9) | (Yte.values > h_ + 1e-9)).any(1).mean())})
pd.DataFrame(sens).to_csv(RES / "02_main_experiments/bounds_sensitivity.csv", index=False); print(pd.DataFrame(sens).round(3))
# SLSQP cross-check on 100 rows
cross = [np.abs(slsqp_projection(Pbest[i], lo, hi) - Pal[i]).max() for i in range(min(100, len(Pbest)))]
eng["slsqp_vs_exact_max_abs_diff"] = float(np.max(cross))
print("engine", eng)

# ---------------------------------------------------------------- A2 cold-start leave-country-out
methods = ["ridge", "rf", "xgb", "lgbm", "cat"]
X, Y = d[FEATURES], d[T]
accum = {}; groups_all = d.iso3.values
rows2 = []
oof_store = {}
for seed in [0, 1]:
    ctry = d.iso3.unique(); rng = np.random.default_rng(seed); perm = rng.permutation(len(ctry))
    fold_of = {c: i % 6 for i, c in zip(range(len(ctry)), ctry[perm])}
    fold = d.iso3.map(fold_of).values
    oof = {k: np.zeros((len(d), len(T))) for k in ["Global mean", "Income-group peer mean"] + [f"ML: {m}" for m in methods] + ["ML Hybrid (50% XGB + 50% CatBoost)"]}
    for f in range(6):
        tri, tei = np.where(fold != f)[0], np.where(fold == f)[0]
        Ytr_f = Y.iloc[tri]
        oof["Global mean"][tei] = Ytr_f.mean().values
        ig = d.iloc[tri].groupby("income_group")[T].mean()
        oof["Income-group peer mean"][tei] = np.vstack([ig.loc[g].values if g in ig.index else Ytr_f.mean().values for g in d.iloc[tei].income_group])
        preds = {}
        for m in methods:
            P = fit_predict_multi(m, X.iloc[tri], Ytr_f, X.iloc[tei], seed=42 + seed)
            preds[m] = P.values; oof[f"ML: {m}"][tei] = P.values
        oof["ML Hybrid (50% XGB + 50% CatBoost)"][tei] = 0.5 * preds["xgb"] + 0.5 * preds["cat"]
    for k, P in oof.items():
        r, t = score(P, Y, groups_all, k); r["seed"] = seed; rows2.append(r)
        if seed == 0: oof_store[k] = t
A2raw = pd.DataFrame(rows2)
agg = A2raw.groupby("method").mean(numeric_only=True).reset_index()
agg["TVD_sd_over_foldseeds"] = A2raw.groupby("method")["TVD"].std().values
A2 = agg.sort_values("TVD"); A2.to_csv(RES / "02_main_experiments/cold_start.csv", index=False)
print(A2[["method", "TVD", "TVD_lo", "TVD_hi", "MAE_pp", "TVD_sd_over_foldseeds"]].round(3).to_string())
best_cold = [m for m in A2.method if m.startswith("ML")][0]
base = oof_store["Income-group peer mean"]; hyb = oof_store["ML Hybrid (50% XGB + 50% CatBoost)"]
dd = base - hyb; lo2, hi2 = boot_ci(dd, groups_all)
A2_paired = {"hybrid_vs_peer_mean_TVD_reduction": float(dd.mean()), "ci95": [lo2, hi2], "best_ML_method": best_cold}

# ---------------------------------------------------------------- A3 feature-group ablation (cold-start, XGB)
groups = {"all features": FEATURES,
          "- governance (WGI)": [f for f in FEATURES if "wgi" in f],
          "- fiscal (tax, debt, expense)": ["tax_revenue_pct_gdp", "central_gov_debt_pct_gdp", "total_expense_pct_gdp"],
          "- demographic/health": ["pop_65plus_pct", "pop_0_14_pct", "urban_pop_pct", "life_expectancy", "under5_mortality"],
          "- macro (GDP, growth, inflation, trade)": ["log_gdp", "gdp_per_capita_usd", "gdp_growth_pct", "inflation_pct", "trade_pct_gdp"],
          "- development/environment (internet, co2, water, structure)": ["internet_users_pct", "electricity_access_pct", "basic_water_access_pct", "co2_per_capita_t", "agri_value_added_pct_gdp", "industry_value_added_pct_gdp"]}
abl = []
for name, drop in groups.items():
    cols = FEATURES if name == "all features" else [f for f in FEATURES if f not in drop]
    ts = []
    for seed in [0, 1]:
        ctry = d.iso3.unique(); rng = np.random.default_rng(seed); perm = rng.permutation(len(ctry))
        fold = d.iso3.map({c: i % 6 for i, c in zip(range(len(ctry)), ctry[perm])}).values
        oofp = np.zeros((len(d), len(T)))
        for f in range(6):
            tri, tei = np.where(fold != f)[0], np.where(fold == f)[0]
            oofp[tei] = fit_predict_multi("xgb", d.iloc[tri][cols], Y.iloc[tri], d.iloc[tei][cols], seed=42 + seed).values
        ts.append(tvd(simplex_renorm(oofp), Y.values).mean())
    abl.append({"variant": name, "n_features": len(cols), "TVD": float(np.mean(ts)), "sd": float(np.std(ts))})
pd.DataFrame(abl).to_csv(RES / "02_main_experiments/ablation.csv", index=False); print(pd.DataFrame(abl).round(3))

json.dump({"A1_paired": A1_paired, "A2_paired": A2_paired, "covid": cov, "engine": eng,
           "panel": {"rows": len(d), "countries": int(d.iso3.nunique()), "A1_train": len(tr), "A1_test": len(te),
                     "A1_test_countries": int(te.iso3.nunique()), "years": [int(d.year.min()), int(d.year.max())]}},
          open(RES / "02_main_experiments/summary.json", "w"), indent=1)
print("done")
