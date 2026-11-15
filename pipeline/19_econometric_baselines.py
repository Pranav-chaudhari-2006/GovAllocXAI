"""Econometric panel baselines for the annual-update regime (a Q1 reviewer will ask for them).
 FE-AR1 : CLR(share_t) = a_c + B CLR(share_{t-1}) + G x_t  (country fixed effects, multi-output ridge with tiny penalty = OLS-like)
 AR1    : same without country fixed effects
 DRIFT  : share_{t-1} + mean historical year-on-year change of the country (random-walk-with-drift)
Protocol identical to 03c history regime: train <=2019 (rows with lag), test 2020-24; cluster-bootstrap CIs; paired gain vs persistence.
Outputs results/14_econometric_baselines/econometric_<panel>.csv and 14_econometric_baselines/summary.json
"""
import importlib.util
import json
import os
import pathlib
import sys

os.environ.setdefault("OMP_NUM_THREADS", "4")
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
from gov_common import *  # noqa: F401,F403

spec = importlib.util.spec_from_file_location("arch21", HERE / "06_stack_architecture.py")
arch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(arch)

clr, inv_clr = arch.clr, arch.inv_clr
summary = {}
for kind in ["A16", "A10"]:
    d, T = arch.load_panel(kind)
    d = d.reset_index(drop=True)
    ok = d.has_lag
    tr, te = d[ok & (d.year <= 2019)], d[ok & (d.year >= 2020)]
    L = [f"h1_{t}" for t in T]
    y_te = te[T].values
    pers = te[L].values
    rows = []

    def add(name, P):
        P = simplex_renorm(np.asarray(P))
        t = tvd(P, y_te)
        lo, hi = boot_ci(t, te.iso3.values)
        base = tvd(simplex_renorm(pers), y_te)
        dlo, dhi = boot_ci(base - t, te.iso3.values)
        rows.append({"method": name, "TVD": float(t.mean()), "TVD_lo": lo, "TVD_hi": hi, "gain_vs_persistence": float((base - t).mean()), "gain_lo": dlo, "gain_hi": dhi, "n": len(te)})

    add("persistence", pers)
    # random walk with drift: mean past change of the country (training years only)
    ch = (tr[T].values - tr[L].values)
    drift = pd.DataFrame(ch, index=tr.index, columns=T).groupby(tr.iso3.values).mean()
    D = np.vstack([drift.loc[i].values if i in drift.index else np.zeros(len(T)) for i in te.iso3])
    add("random walk with drift", pers + D)

    imp, sc = SimpleImputer(strategy="median").fit(tr[FEATURES]), None
    sc = StandardScaler().fit(imp.transform(tr[FEATURES]))
    def design(df, fe):
        Xm = sc.transform(imp.transform(df[FEATURES]))
        parts = [clr(df[L].values), Xm]
        if fe:
            parts.append(pd.get_dummies(df.iso3).reindex(columns=fe, fill_value=0).values.astype(float))
        return np.hstack(parts)
    fe_cols = sorted(tr.iso3.unique())
    for name, fe in [("AR(1) panel, pooled (CLR)", None), ("AR(1) panel + country fixed effects (CLR)", fe_cols)]:
        for alpha in [1.0, 10.0]:
            m = Ridge(alpha=alpha).fit(design(tr, fe), clr(tr[T].values))
            add(f"{name}, ridge alpha={alpha:g}", inv_clr(m.predict(design(te, fe))))
    R = pd.DataFrame(rows)
    R.to_csv(RES / f"14_econometric_baselines/econometric_{kind}.csv", index=False)
    print(kind, "\n", R.round(3).to_string(), flush=True)
    summary[kind] = R.to_dict("records")
json.dump(summary, open(RES / "14_econometric_baselines/summary.json", "w"), indent=1, default=float)
