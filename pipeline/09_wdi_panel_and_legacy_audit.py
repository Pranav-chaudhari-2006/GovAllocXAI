"""Experiment B: global WDI panel (4 official sector targets x 2 units) and Experiment C: forensic re-analysis of legacy v1 results.
Outputs: results/03_wdi_panel/*.csv, results/01_legacy_audit/legacy_audit.json
"""
import json, sys
import numpy as np, pandas as pd
from sklearn.model_selection import GroupKFold
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from gov_common import *
from xgboost import XGBRegressor

# ======================================================== C. legacy audit
leg = pd.read_csv(OLD / "govallocxai_old_dataset.csv")
LEG_F = ['population', 'urban_population_percent', 'gdp_usd', 'gdp_per_capita_usd', 'gdp_growth_percent', 'inflation_percent', 'tax_revenue_usd',
         'government_debt_usd', 'poverty_rate_percent', 'unemployment_rate_percent', 'literacy_rate_percent', 'life_expectancy_years',
         'health_expenditure_usd', 'internet_users_percent', 'electricity_access_percent', 'co2_emissions', 'corruption_index', 'government_effectiveness']
LEG_T = ['defence_usd', 'infrastructure_usd', 'research_and_development_usd', 'education_usd', 'healthcare_usd', 'agriculture_usd',
         'rural_development_usd', 'social_welfare_freebies_usd', 'energy_usd', 'transport_usd', 'housing_urban_development_usd',
         'water_sanitation_usd', 'environment_climate_usd', 'digital_it_usd', 'industry_msme_usd']
C = {}
num = leg.select_dtypes("number")
ident = [(a, b) for i, a in enumerate(num.columns) for b in num.columns[i + 1:] if np.allclose(num[a], num[b], rtol=1e-9)]
C["identical_column_pairs"] = ident
tg_ident = [(a, b) for a, b in ident if a in LEG_T or b in LEG_T]
C["identical_pairs_involving_targets"] = len(tg_ident)
ratio = leg[LEG_T].div(leg.gdp_usd, axis=0)
C["ratio_to_gdp"] = {t: {"mean_pct": float(ratio[t].mean() * 100), "cv": float(ratio[t].std() / ratio[t].mean()),
                          "within_country_cv": float((ratio[t].groupby(leg.country).std() / ratio[t].groupby(leg.country).mean()).median())} for t in LEG_T}
C["n_targets_cv_below_0.05"] = int(sum(v["cv"] < 0.05 for v in C["ratio_to_gdp"].values()))
cc = leg[LEG_T].corr().values; C["target_corr_offdiag_min_mean"] = [float(cc[np.triu_indices(15, 1)].min()), float(cc[np.triu_indices(15, 1)].mean())]
C["healthcare_equals_feature_health_expenditure"] = bool(np.allclose(leg.healthcare_usd, leg.health_expenditure_usd))
rng = np.random.default_rng(42); idx = rng.permutation(len(leg)); cut = int(.8 * len(leg))
from sklearn.model_selection import train_test_split
Xtr, Xte, Ytr, Yte = train_test_split(leg[LEG_F], leg[LEG_T], test_size=0.2, random_state=42)


def xg(): return XGBRegressor(n_estimators=500, learning_rate=0.03, max_depth=6, subsample=0.8, colsample_bytree=0.8, random_state=42, n_jobs=-1, verbosity=0)


def r2(y, p): return 1 - ((y - p) ** 2).sum() / ((y - y.mean()) ** 2).sum()
res = {"xgb_random_split_R2_usd": {}, "formula_k_x_gdp_R2_usd": {}, "xgb_ratio_scale_R2": {}, "const_ratio_R2": {}}
for t in LEG_T:
    m = xg().fit(Xtr, Ytr[t]); res["xgb_random_split_R2_usd"][t] = float(r2(Yte[t], m.predict(Xte)))
    k = (Ytr[t] / Xtr.gdp_usd).median(); res["formula_k_x_gdp_R2_usd"][t] = float(r2(Yte[t], k * Xte.gdp_usd))
    ytr_r, yte_r = Ytr[t] / Xtr.gdp_usd, Yte[t] / Xte.gdp_usd
    mr = xg().fit(Xtr, ytr_r); res["xgb_ratio_scale_R2"][t] = float(r2(yte_r, mr.predict(Xte)))
    res["const_ratio_R2"][t] = float(r2(yte_r, np.full(len(yte_r), ytr_r.median())))
for k in list(res): res[k + "_mean"] = float(np.mean(list(res[k].values())))
C["replication"] = res
# leakage: healthcare with/without the identical feature
nf = [f for f in LEG_F if f != "health_expenditure_usd"]
m_with = xg().fit(Xtr, Ytr.healthcare_usd); m_wo = xg().fit(Xtr[nf], Ytr.healthcare_usd)
C["healthcare_R2_with_leaky_feature"] = float(r2(Yte.healthcare_usd, m_with.predict(Xte)))
C["healthcare_R2_without_leaky_feature"] = float(r2(Yte.healthcare_usd, m_wo.predict(Xte[nf])))
# temporal split on legacy
trm, tem = leg.year <= 2019, leg.year >= 2020
tr_t = {t: float(r2(leg.loc[tem, t], xg().fit(leg.loc[trm, LEG_F], leg.loc[trm, t]).predict(leg.loc[tem, LEG_F]))) for t in LEG_T}
C["temporal_split_xgb_R2_usd_mean"] = float(np.mean(list(tr_t.values())))
tr_k = {t: float(r2(leg.loc[tem, t], (leg.loc[trm, t] / leg.loc[trm, "gdp_usd"]).median() * leg.loc[tem, "gdp_usd"])) for t in LEG_T}
C["temporal_split_formula_R2_usd_mean"] = float(np.mean(list(tr_k.values())))
# legacy vs official (real) targets for the 4 sectors that have an official counterpart
m = pd.read_csv(PROC / "govallocxai_new_master.csv"); m = m[m.has_legacy_v1_row == 1]
off = {}
for lt, w in [("defence_usd", "wdi_defence_pct_gdp"), ("education_usd", "wdi_education_pct_gdp"), ("healthcare_usd", "wdi_health_pct_gdp"), ("research_and_development_usd", "wdi_rnd_pct_gdp")]:
    q = pd.DataFrame({"leg": m[f"legacy_{lt}"] / m["legacy_gdp_usd"] * 100, "off": m[w]}).dropna()
    off[lt] = {"n": int(len(q)), "pearson": float(np.corrcoef(q.leg, q.off)[0, 1]), "median_abs_err_pp": float((q.leg - q.off).abs().median())}
C["legacy_vs_official"] = off
json.dump(C, open(RES / "01_legacy_audit/legacy_audit.json", "w"), indent=1)
print("LEGACY:", json.dumps({k: v for k, v in C.items() if k not in ("ratio_to_gdp", "replication", "identical_column_pairs")}, indent=1)[:2500])
print("replication means", {k: v for k, v in res.items() if k.endswith("_mean")})

# ======================================================== B. WDI global panel
w = pd.read_csv(PROC / "govallocxai_new_wdi_panel.csv").sort_values(["iso3", "year"]).reset_index(drop=True)
WT = ["wdi_education_pct_gdp", "wdi_health_pct_gdp", "wdi_defence_pct_gdp", "wdi_rnd_pct_gdp",
      "wdi_education_pct_govexp", "wdi_health_pct_govexp", "wdi_defence_pct_govexp"]
rows = []


def add(target, protocol, method, y, p, g=None, extra=None):
    mm = regression_metrics(y, p); r = {"target": target, "protocol": protocol, "method": method, "n": len(y), **mm}
    if extra: r.update(extra)
    rows.append(r)


for tgt in WT:
    lag = w.groupby("iso3")[tgt].shift(1); ok_lag = (w.year - w.groupby("iso3")["year"].shift(1)) == 1
    w[f"lag_{tgt}"] = lag.where(ok_lag)
    sub = w[w[tgt].notna()].copy()
    # ---- B1 temporal with history
    tr, te = sub[(sub.year <= 2018)], sub[(sub.year >= 2019) & sub[f"lag_{tgt}"].notna()]
    trl = tr[tr[f"lag_{tgt}"].notna()]
    y = te[tgt].values
    add(tgt, "B1 temporal+history", "Persistence", y, te[f"lag_{tgt}"].values)
    cmn = tr.groupby("iso3")[tgt].mean(); add(tgt, "B1 temporal+history", "Country mean", y, te.iso3.map(cmn).fillna(tr[tgt].mean()).values)
    add(tgt, "B1 temporal+history", "Global mean", y, np.full(len(y), tr[tgt].mean()))
    Y1 = trl[[tgt]]; ps = {}
    for mname in ["ridge", "rf", "xgb", "lgbm", "cat"]:
        P = fit_predict_multi(mname, tr[FEATURES], tr[[tgt]], te[FEATURES]).values[:, 0]
        add(tgt, "B1 temporal+history", f"ML features-only: {mname}", y, P)
        D = fit_predict_multi(mname, trl[FEATURES + [f"lag_{tgt}"]], (trl[tgt] - trl[f"lag_{tgt}"]).to_frame(tgt),
                              te[FEATURES + [f"lag_{tgt}"]]).values[:, 0]
        ps[mname] = D; add(tgt, "B1 temporal+history", f"Delta-ML: {mname}", y, te[f"lag_{tgt}"].values + D)
    add(tgt, "B1 temporal+history", "Delta-ML Hybrid (XGB+Cat)", y, te[f"lag_{tgt}"].values + 0.5 * ps["xgb"] + 0.5 * ps["cat"])
    # ---- B2 grouped country CV (cold start)  &  B3 leave-region-out
    for proto, fold in [("B2 leave-country-out", None), ("B3 leave-region-out", "region")]:
        if fold is None:
            ctry = sub.iso3.unique(); perm = np.random.default_rng(0).permutation(len(ctry))
            fid = sub.iso3.map({c: i % 6 for i, c in zip(range(len(ctry)), ctry[perm])}).values
        else:
            regs = {r: i for i, r in enumerate(sub.region.unique())}; fid = sub.region.map(regs).values
        oof = {k: np.zeros(len(sub)) for k in ["Global mean", "Income-group peer mean", "ridge", "rf", "xgb", "lgbm", "cat", "Hybrid (XGB+Cat)"]}
        for f in np.unique(fid):
            a, b = np.where(fid != f)[0], np.where(fid == f)[0]
            trf, tef = sub.iloc[a], sub.iloc[b]
            oof["Global mean"][b] = trf[tgt].mean()
            ig = trf.groupby("income_group")[tgt].mean(); oof["Income-group peer mean"][b] = tef.income_group.map(ig).fillna(trf[tgt].mean()).values
            for mname in ["ridge", "rf", "xgb", "lgbm", "cat"]:
                oof[mname][b] = fit_predict_multi(mname, trf[FEATURES], trf[[tgt]], tef[FEATURES]).values[:, 0]
            oof["Hybrid (XGB+Cat)"][b] = 0.5 * oof["xgb"][b] + 0.5 * oof["cat"][b]
        for k, P in oof.items():
            add(tgt, proto, k if k in ("Global mean", "Income-group peer mean", "Hybrid (XGB+Cat)") else f"ML: {k}", sub[tgt].values, P)
    print("done", tgt, flush=True)
B = pd.DataFrame(rows); B.to_csv(RES / "03_wdi_panel/wdi_results.csv", index=False)
print(B[B.protocol.str.startswith("B2")].pivot(index="method", columns="target", values="R2").round(3).to_string())
print("done")
