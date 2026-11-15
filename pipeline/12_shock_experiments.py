"""Shock-aware Delta-learner evaluation (expH).

Question: do contemporaneous shock features (country growth/unemployment/inflation/debt changes, recession dummy, severity,
cross-country median growth in the same year and its interaction with the lagged share) help the annual-update Delta-learner
anticipate shock years (COVID 2020-21, GFC 2009-10)?

Methods (target = share_t - share_{t-1}; prediction = lag + Delta, then simplex renormalisation):
  persistence | delta_xgb_base | delta_cat_base | delta_xgb_shock | delta_cat_shock | delta_xgb_regime (recession-only sub-model)
Protocols: (a) train<=2019 (rows with lag) -> test 2020-24 ; (b) train<=2007 -> test 2009-2010 (2008 skipped).
Outputs: results/08_shock_experiments/shock_<panel>.csv (TVD + paired gains), results/08_shock_experiments/shock_<panel>_sectors.csv (health / social protection
in shock years), results/08_shock_experiments/summary.json.
Usage: python pipeline/12_shock_experiments.py [A16|A10|both]
"""
import os
os.environ["OMP_NUM_THREADS"] = "4"
import json
import pathlib
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from gov_common import *  # noqa: F401,F403
import importlib.util

_spec = importlib.util.spec_from_file_location("arch21", str(pathlib.Path(__file__).parent / "06_stack_architecture.py"))
arch = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(arch)

KEY = {"A16": {"health": "cofog_health_pct_total", "social_protection": "cofog_social_protection_pct_total"},
       "A10": {"health": "cofog10_GF07_pct_total", "social_protection": "cofog10_GF10_pct_total"}}
METHODS = ["persistence", "delta_xgb_base", "delta_cat_base", "delta_xgb_shock", "delta_cat_shock", "delta_xgb_regime"]


def add_shock_features(d, T):
    """Shock features from year-t macros, year t-1 macros of the same country, and same-year cross-country medians."""
    d = d.sort_values(["iso3", "year"]).reset_index(drop=True)
    g = d.groupby("iso3")
    consec = (d.year - g["year"].shift(1)) == 1
    new = {}
    for src, nm in [("gdp_growth_pct", "d_growth"), ("unemployment_pct", "d_unemp"), ("inflation_pct", "d_infl"),
                    ("central_gov_debt_pct_gdp", "d_debt")]:
        new[nm] = (d[src] - g[src].shift(1)).where(consec)
    new["recession"] = (d.gdp_growth_pct < 0).astype(float).where(d.gdp_growth_pct.notna())
    new["severity"] = d.gdp_growth_pct.clip(upper=0)
    med = d.groupby("year").gdp_growth_pct.median()          # contemporaneous cross-country median (same-year macro input)
    new["glob_growth"] = d.year.map(med)
    new["glob_dgrowth"] = d.year.map(med - med.shift(1))
    new["glob_recession"] = (new["glob_growth"] < 0).astype(float)
    N = pd.DataFrame(new)
    for t in T:
        N[f"gx_{t}"] = N["glob_growth"] * d[f"h1_{t}"]
    sf = list(N.columns)
    d = pd.concat([d.drop(columns=[c for c in N.columns if c in d.columns]), N], axis=1)
    return d, sf


def run_methods(d, T, tr, te, sf):
    h1 = [f"h1_{t}" for t in T]
    Xb = FEATURES + h1
    Xs = Xb + sf
    L = te[h1].values
    D = pd.DataFrame(tr[T].values - tr[h1].values, columns=T, index=tr.index)
    out = {"persistence": L}
    out["delta_xgb_base"] = L + fit_predict_multi("xgb", tr[Xb], D, te[Xb]).values
    out["delta_cat_base"] = L + fit_predict_multi("cat", tr[Xb], D, te[Xb]).values
    out["delta_xgb_shock"] = L + fit_predict_multi("xgb", tr[Xs], D, te[Xs]).values
    out["delta_cat_shock"] = L + fit_predict_multi("cat", tr[Xs], D, te[Xs]).values
    # regime split: recession-year rows (country growth<0) use a model trained only on recession rows (if enough data)
    P = out["delta_xgb_shock"].copy()
    rtr, rte = tr.recession == 1, (te.recession == 1).values
    if rtr.sum() >= 40 and rte.any():
        Pr = L[rte] + fit_predict_multi("xgb", tr.loc[rtr, Xs], D[rtr], te.loc[rte, Xs]).values
        P[rte] = Pr
    out["delta_xgb_regime"] = P
    out["_n_recession_train"] = int(rtr.sum())
    return out


def summarise(kind, proto, te, T, preds, rows, sec_rows, summ):
    A = te[T].values
    L = te[[f"h1_{t}" for t in T]].values
    ysub = {"all": np.ones(len(te), bool)}
    if proto == "a_covid":
        ysub.update({"2020": (te.year == 2020).values, "2021": (te.year == 2021).values, "2020-21": te.year.isin([2020, 2021]).values,
                     "2022-24": (te.year >= 2022).values})
    else:
        ysub.update({"2009": (te.year == 2009).values, "2010": (te.year == 2010).values})
    tv = {m: tvd(simplex_renorm(preds[m]), A) for m in METHODS}
    g = te.iso3.values
    for sub, msk in ysub.items():
        if msk.sum() == 0:
            continue
        for m in METHODS:
            x = tv[m][msk]; lo, hi = boot_ci(x, g[msk])
            r = {"panel": kind, "protocol": proto, "subset": sub, "method": m, "n": int(msk.sum()), "n_economies": int(len(set(g[msk]))),
                 "TVD": float(x.mean()), "TVD_lo": lo, "TVD_hi": hi}
            for ref in ["persistence", "delta_xgb_base", "delta_cat_base"]:
                gain = tv[ref][msk] - x
                if m == ref:
                    continue
                glo, ghi = boot_ci(gain, g[msk])
                r[f"gain_vs_{ref}"] = float(gain.mean()); r[f"gain_vs_{ref}_lo"] = glo; r[f"gain_vs_{ref}_hi"] = ghi
            rows.append(r)
    # sector diagnostics in shock years
    shock_years = [2020, 2021] if proto == "a_covid" else [2009, 2010]
    for yr in shock_years + ["pooled"]:
        msk = te.year.isin(shock_years).values if yr == "pooled" else (te.year == yr).values
        if msk.sum() == 0:
            continue
        for sec, col in KEY[kind].items():
            k = T.index(col)
            act = (A[:, k] - L[:, k])[msk]
            for m in METHODS:
                if m == "persistence":
                    continue
                pred = (simplex_renorm(preds[m])[:, k] - L[:, k])[msk]
                corr = float(np.corrcoef(pred, act)[0, 1]) if pred.std() > 0 and act.std() > 0 else float("nan")
                nz = act != 0
                sec_rows.append({"panel": kind, "protocol": proto, "year": yr, "sector": sec, "method": m, "n": int(msk.sum()),
                                 "mean_actual_change_pp": float(act.mean()), "mean_pred_change_pp": float(pred.mean()),
                                 "corr_pred_actual_change": corr, "directional_accuracy": float((np.sign(pred[nz]) == np.sign(act[nz])).mean()),
                                 "share_actual_up": float((act > 0).mean())})
    return tv


def run_panel(kind):
    d, T = arch.load_panel(kind)
    d, sf = add_shock_features(d, T)
    ok = d.has_lag
    rows, sec_rows, summ = [], [], {}
    protos = {"a_covid": (d[ok & (d.year <= 2019)], d[ok & (d.year >= 2020)]),
              "b_gfc": (d[ok & (d.year <= 2007)], d[ok & (d.year >= 2009) & (d.year <= 2010)])}
    for proto, (tr, te) in protos.items():
        print(kind, proto, "train", len(tr), "test", len(te), "economies", te.iso3.nunique(), flush=True)
        preds = run_methods(d, T, tr, te, sf)
        ntr = preds.pop("_n_recession_train")
        summarise(kind, proto, te, T, preds, rows, sec_rows, summ)
        summ[proto] = {"n_train": len(tr), "n_test": len(te), "n_test_economies": int(te.iso3.nunique()), "n_recession_rows_train": ntr,
                       "test_years": sorted(map(int, te.year.unique())),
                       "train_global_median_growth_neg_years": sorted(int(y) for y in tr.year.unique() if tr.loc[tr.year == y, "glob_growth"].iloc[0] < 0)}
    R = pd.DataFrame(rows); R.to_csv(RES / f"08_shock_experiments/shock_{kind}.csv", index=False)
    S = pd.DataFrame(sec_rows); S.to_csv(RES / f"08_shock_experiments/shock_{kind}_sectors.csv", index=False)
    print(R[R.subset.isin(["all", "2020-21", "2009", "2010"])][["protocol", "subset", "method", "n", "TVD", "TVD_lo", "TVD_hi", "gain_vs_persistence", "gain_vs_delta_xgb_base"]].round(3).to_string(), flush=True)
    print(S[S.year == "pooled"].round(3).to_string(), flush=True)
    summ["features_added"] = sf[:10] + ["gx_<target> (glob_growth x lagged share)"]
    summ["results"] = R.to_dict("records")
    summ["sector_pooled_shock_years"] = S[S.year == "pooled"].to_dict("records")
    return summ


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    out = {}
    for kind in (["A16", "A10"] if which == "both" else [which]):
        out[kind] = run_panel(kind)
    fn = RES / "08_shock_experiments/summary.json"
    old = json.load(open(fn)) if fn.exists() else {}
    old.update(out)
    json.dump(old, open(fn, "w"), indent=1, default=float)
    print("done")
