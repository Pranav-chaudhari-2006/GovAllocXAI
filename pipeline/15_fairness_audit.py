"""Fairness / group-error audit of the leave-country-out (cold-start) predictions.

Panel A10 (10 COFOG divisions, original strict panel): XGBoost raw targets, 6 folds grouped by country, seed 0, vs income-group peer mean.
Panel B (WDI health / education / defence / R&D, % of GDP): same cold-start protocol, XGBoost vs income-group peer mean.
Groups: World Bank income group and region.  Metrics: TVD, per-target MAE, worst-group error, max/min ratio (disparate error ratio),
SIGNED bias (pred - actual, pp) per division per group, need-vs-allocation diagnostic.  All CIs are cluster (country) bootstraps.
Outputs: results/12_fairness_audit/*.csv, results/12_fairness_audit/summary.json
"""
import os
os.environ["OMP_NUM_THREADS"] = "4"
import json
import pathlib
import sys

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from gov_common import *  # noqa: F401,F403

INCS = ["Low income", "Lower middle income", "Upper middle income", "High income"]
DIV = [f"GF{i:02d}" for i in range(1, 11)]
T = [f"cofog10_{g}_pct_total" for g in DIV]
DIVNAME = dict(zip(DIV, ["General public services", "Defence", "Public order & safety", "Economic affairs", "Environment protection",
                         "Housing & community", "Health", "Recreation & culture", "Education", "Social protection"]))
S = {}
rng = np.random.default_rng(0)


def cboot(x, g, n=2000, seed=0):
    return boot_ci(np.asarray(x, float), np.asarray(g), n=n, seed=seed)


def ratio_ci(vals_by_group, iso_by_group, n=1000, seed=0):
    """cluster bootstrap (stratified by group) of max/min of group means."""
    r = np.random.default_rng(seed)
    pre = {}
    for k in vals_by_group:
        s = pd.Series(vals_by_group[k]).groupby(iso_by_group[k]).agg(["sum", "count"])
        pre[k] = (s["sum"].values, s["count"].values)
    out = []
    for _ in range(n):
        m = []
        for k, (sm, ct) in pre.items():
            i = r.integers(0, len(sm), len(sm))
            m.append(sm[i].sum() / ct[i].sum())
        out.append(max(m) / min(m))
    return float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))


def folds(d, seed=0):
    ctry = d.iso3.unique()
    perm = np.random.default_rng(seed).permutation(len(ctry))
    return d.iso3.map({c: i % 6 for i, c in zip(range(len(ctry)), ctry[perm])}).values


def xgb_multi(Xtr, Ytr, Xte, seed=42):
    """identical to gov_common.fit_predict_multi('xgb') but with n_jobs=2 (shared CPU)."""
    mu, sd = Ytr.mean(0), Ytr.std(0).replace(0, 1)
    Z = (Ytr - mu) / sd
    out = []
    for c in Ytr.columns:
        m = make_model("xgb", seed); m.set_params(n_jobs=2)
        m.fit(Xtr, Z[c]); out.append(m.predict(Xte))
    return (pd.DataFrame(np.column_stack(out), columns=Ytr.columns, index=Xte.index) * sd + mu).values


# ============================================================ Panel A10
d = pd.read_csv(PROC / "govallocxai_new_cofog10_panel.csv").sort_values(["iso3", "year"]).reset_index(drop=True)
X, Y = d[FEATURES], d[T]
fold = folds(d, 0)          # identical to 07_cold_start_by_income.py
P = {"xgb": np.zeros((len(d), 10)), "peer_mean": np.zeros((len(d), 10))}
for f in range(6):
    a, b = np.where(fold != f)[0], np.where(fold == f)[0]
    ig = d.iloc[a].groupby("income_group")[T].mean()
    P["peer_mean"][b] = np.vstack([ig.loc[g].values if g in ig.index else Y.iloc[a].mean().values for g in d.iloc[b].income_group])
    P["xgb"][b] = xgb_multi(X.iloc[a], Y.iloc[a], X.iloc[b])
    print("A10 fold", f, flush=True)
Yv = Y.values
PR = {k: simplex_renorm(v) for k, v in P.items()}
E = {k: PR[k] - Yv for k in PR}                       # signed error (pp)
TV = {k: tvd(PR[k], Yv) for k in PR}
d["region_g"] = d.region
reg_n = d.groupby("region").iso3.nunique()
S["A10"] = {"n_rows": len(d), "n_economies": int(d.iso3.nunique()), "overall_TVD": {k: float(TV[k].mean()) for k in TV}}

grp_rows, bias_rows = [], []
for gcol, order in [("income_group", INCS), ("region", sorted(d.region.unique()))]:
    vals, isos = {}, {}
    for g in order:
        m = (d[gcol] == g).values
        if not m.any():
            continue
        r = {"panel": "A10", "group_type": gcol, "group": g, "economies": int(d.iso3[m].nunique()), "country_years": int(m.sum())}
        for k in TV:
            lo, hi = cboot(TV[k][m], d.iso3[m])
            r[f"TVD_{k}"], r[f"lo_{k}"], r[f"hi_{k}"] = float(TV[k][m].mean()), lo, hi
            r[f"MAE_per_target_{k}"] = float(np.abs(E[k][m]).mean())
        dlt = TV["xgb"][m] - TV["peer_mean"][m]
        lo, hi = cboot(dlt, d.iso3[m])
        r["TVD_xgb_minus_peer"], r["lo_diff"], r["hi_diff"] = float(dlt.mean()), lo, hi
        grp_rows.append(r)
        vals[g], isos[g] = TV["xgb"][m], d.iso3[m].values
        for j, gf in enumerate(DIV):
            for k in E:
                x = E[k][m, j]
                lo, hi = cboot(x, d.iso3[m], n=1000)
                bias_rows.append({"panel": "A10", "group_type": gcol, "group": g, "economies": int(d.iso3[m].nunique()), "division": gf,
                                  "division_name": DIVNAME[gf], "model": k, "mean_actual": float(Yv[m, j].mean()),
                                  "mean_pred": float(PR[k][m, j].mean()), "bias_pp": float(x.mean()), "lo": lo, "hi": hi,
                                  "rel_bias_pct": float(x.mean() / Yv[m, j].mean() * 100), "MAE_pp": float(np.abs(x).mean())})
    big = [g for g in vals if d.iso3[d[gcol] == g].nunique() >= 3]
    gm = {g: vals[g].mean() for g in big}
    w, bst = max(gm, key=gm.get), min(gm, key=gm.get)
    lo, hi = ratio_ci({g: vals[g] for g in big}, {g: isos[g] for g in big})
    gm_p = {g: TV["peer_mean"][(d[gcol] == g).values].mean() for g in big}
    S["A10"][f"disparity_{gcol}"] = {"groups_used(>=3 economies)": big, "worst_group": w, "worst_TVD": float(gm[w]), "best_group": bst, "best_TVD": float(gm[bst]),
                                      "max_min_ratio_xgb": float(gm[w] / gm[bst]), "ratio_ci95": [lo, hi],
                                      "max_min_ratio_peer_mean": float(max(gm_p.values()) / min(gm_p.values())),
                                      "worst_group_peer_mean": max(gm_p, key=gm_p.get), "worst_TVD_peer_mean": float(max(gm_p.values()))}
G = pd.DataFrame(grp_rows)
Bf = pd.DataFrame(bias_rows)
G.to_csv(RES / "12_fairness_audit/A10_group_error.csv", index=False)
Bf.to_csv(RES / "12_fairness_audit/A10_signed_bias.csv", index=False)
print(G[["group_type", "group", "economies", "country_years", "TVD_xgb", "lo_xgb", "hi_xgb", "TVD_peer_mean", "TVD_xgb_minus_peer"]].round(2).to_string())
bi = Bf[(Bf.group_type == "income_group") & (Bf.model == "xgb") & Bf.division.isin(["GF07", "GF09", "GF10"])]
print(bi[["group", "division", "mean_actual", "mean_pred", "bias_pp", "lo", "hi"]].round(2).to_string())

# per-target MAE by income group
mae = []
for g in INCS:
    m = (d.income_group == g).values
    for j, gf in enumerate(DIV):
        mae.append({"income_group": g, "division": gf, "MAE_xgb": float(np.abs(E["xgb"][m, j]).mean()), "MAE_peer": float(np.abs(E["peer_mean"][m, j]).mean())})
pd.DataFrame(mae).to_csv(RES / "12_fairness_audit/A10_mae_by_target.csv", index=False)

# ---- need vs allocation diagnostic (country-level means within income group)
need = []
pairs = [("GF07", "health", "under5_mortality"), ("GF09", "education", "pop_0_14_pct")]
for gf, nm, nv in pairs:
    j = DIV.index(gf)
    for g in INCS:
        m = (d.income_group == g).values
        c = pd.DataFrame({"iso3": d.iso3[m].values, "need": d[nv][m].values, "actual": Yv[m, j], "pred": PR["xgb"][m, j], "peer": PR["peer_mean"][m, j]}).groupby("iso3").mean()
        r = {"division": gf, "area": nm, "need_proxy": nv, "income_group": g, "economies": len(c)}
        if len(c) >= 4:
            def sp(a, b):
                return float(spearmanr(a, b)[0])
            for lab, col in [("actual", "actual"), ("pred_xgb", "pred")]:
                r[f"rho_need_{lab}"] = sp(c.need, c[col])
            r["rho_pred_actual"] = sp(c.pred, c.actual)
            bs = []
            rr = np.random.default_rng(1)
            for _ in range(1000):
                i = rr.integers(0, len(c), len(c))
                cc = c.iloc[i]
                if cc.need.nunique() < 2 or cc.actual.nunique() < 2 or cc.pred.nunique() < 2:
                    continue
                bs.append(spearmanr(cc.need, cc.pred)[0] - spearmanr(cc.need, cc.actual)[0])
            r["delta_rho_pred_minus_actual_lo"], r["delta_rho_pred_minus_actual_hi"] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))] if bs else [np.nan, np.nan]
        need.append(r)
    # pooled across all groups, row level
    c = pd.DataFrame({"need": d[nv].values, "actual": Yv[:, j], "pred": PR["xgb"][:, j]})
    need.append({"division": gf, "area": nm, "need_proxy": nv, "income_group": "ALL (rows)", "economies": int(d.iso3.nunique()),
                 "rho_need_actual": float(spearmanr(c.need, c.actual)[0]), "rho_need_pred_xgb": float(spearmanr(c.need, c.pred)[0]),
                 "rho_pred_actual": float(spearmanr(c.pred, c.actual)[0])})
NV = pd.DataFrame(need)
NV.to_csv(RES / "12_fairness_audit/need_vs_allocation.csv", index=False)
print(NV.round(2).to_string())

# ============================================================ Panel B (WDI % GDP)
w = pd.read_csv(PROC / "govallocxai_new_wdi_panel.csv", low_memory=False).sort_values(["iso3", "year"]).reset_index(drop=True)
WT = {"wdi_health_pct_gdp": "health", "wdi_education_pct_gdp": "education", "wdi_defence_pct_gdp": "defence", "wdi_rnd_pct_gdp": "R&D"}
brows = []
for t, nm in WT.items():
    dd = w.dropna(subset=[t]).reset_index(drop=True)
    from xgboost import XGBRegressor
    fo = folds(dd, 0)
    pr = np.zeros(len(dd)); pm = np.zeros(len(dd))
    y = dd[t].values
    for f in range(6):
        a, b = np.where(fo != f)[0], np.where(fo == f)[0]
        mdl = make_model("xgb", 42); mdl.set_params(n_jobs=2)
        mdl.fit(dd[FEATURES].iloc[a], y[a])
        pr[b] = mdl.predict(dd[FEATURES].iloc[b])
        ig = dd.iloc[a].groupby("income_group")[t].mean()
        pm[b] = dd.income_group.iloc[b].map(ig).fillna(y[a].mean()).values
    for gcol, order in [("income_group", INCS), ("region", sorted(dd.region.unique()))]:
        for g in order:
            m = (dd[gcol] == g).values
            if m.sum() < 5:
                continue
            r = {"panel": "B", "target": nm, "group_type": gcol, "group": g, "economies": int(dd.iso3[m].nunique()), "country_years": int(m.sum()),
                 "mean_actual_pct_gdp": float(y[m].mean())}
            for k, p in [("xgb", pr), ("peer_mean", pm)]:
                e = p[m] - y[m]
                lo, hi = cboot(np.abs(e), dd.iso3[m], n=1000)
                blo, bhi = cboot(e, dd.iso3[m], n=1000)
                r[f"MAE_{k}"], r[f"MAE_lo_{k}"], r[f"MAE_hi_{k}"] = float(np.abs(e).mean()), lo, hi
                r[f"bias_{k}"], r[f"bias_lo_{k}"], r[f"bias_hi_{k}"] = float(e.mean()), blo, bhi
            r["rel_MAE_xgb_pct_of_mean"] = r["MAE_xgb"] / r["mean_actual_pct_gdp"] * 100
            brows.append(r)
BB = pd.DataFrame(brows)
BB.to_csv(RES / "12_fairness_audit/B_wdi_group_error.csv", index=False)
print(BB[BB.group_type == "income_group"][["target", "group", "economies", "mean_actual_pct_gdp", "MAE_xgb", "MAE_peer_mean", "bias_xgb", "bias_lo_xgb", "bias_hi_xgb"]].round(2).to_string())
S["B"] = {}
for t, nm in WT.items():
    q = BB[(BB.target == nm) & (BB.group_type == "income_group")]
    q = q[q.economies >= 3]
    S["B"][nm] = {"worst_group_MAE": q.loc[q.MAE_xgb.idxmax(), "group"], "worst_MAE": float(q.MAE_xgb.max()), "best_MAE": float(q.MAE_xgb.min()),
                  "ratio_MAE": float(q.MAE_xgb.max() / q.MAE_xgb.min()),
                  "rel_MAE_ratio_pct_of_mean": float((q.MAE_xgb / q.mean_actual_pct_gdp).max() / (q.MAE_xgb / q.mean_actual_pct_gdp).min()),
                  "bias_by_income": {r.group: round(float(r.bias_xgb), 3) for r in q.itertuples()}}
json.dump(S, open(RES / "12_fairness_audit/summary.json", "w"), indent=1, default=str)
print(json.dumps(S, indent=1, default=str))
