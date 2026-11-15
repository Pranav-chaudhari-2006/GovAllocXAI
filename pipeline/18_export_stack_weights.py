"""Export production stack weights for the API (cold-start Stack v2.1).
For each panel (A16 -> 'cofog16', A10 -> 'cofog10'): grouped 5-fold out-of-fold predictions of the members
[peer_mean, ridge, xgb_clr, cat_clr] on ALL rows, then per-component non-negative least-squares weights (sum 1).
Output: backend/stack_weights.json  {panel: {"members": [...], "components": [...], "weights": [[...per component...] per member]}}
The API refits the members on all rows at start-up and blends them with these weights; SHAP/LIME explain the XGBoost member.
"""
import importlib.util
import json
import os
import pathlib
import sys

os.environ.setdefault("OMP_NUM_THREADS", "4")
import numpy as np
import pandas as pd

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
from gov_common import *  # noqa: F401,F403

spec = importlib.util.spec_from_file_location("arch21", HERE / "06_stack_architecture.py")
arch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(arch)

MEMBERS = ["peer_mean", "ridge", "xgb_clr", "cat_clr"]
out = {}
for kind, key in [("A16", "cofog16"), ("A10", "cofog10")]:
    d, T = arch.load_panel(kind)
    d = d.reset_index(drop=True)
    X, Y = d[FEATURES], d[T]
    ctry = d.iso3.unique()
    perm = np.random.default_rng(0).permutation(len(ctry))
    fold = d.iso3.map({c: i % 5 for i, c in zip(range(len(ctry)), ctry[perm])}).values
    oof = {m: np.zeros((len(d), len(T))) for m in MEMBERS}
    for f in range(5):
        a, b = np.where(fold != f)[0], np.where(fold == f)[0]
        P = arch.cold_fold_preds(X.iloc[a], Y.iloc[a], X.iloc[b], d.iloc[a], d.iloc[b], T, 42)
        for m in MEMBERS:
            oof[m][b] = P[m]
        print(kind, "fold", f, "done", flush=True)
    W = arch.nnls_weights([oof[m] for m in MEMBERS], Y.values)
    tv = {m: float(tvd(simplex_renorm(oof[m]), Y.values).mean()) for m in MEMBERS}
    tv["stack"] = float(tvd(simplex_renorm(arch.combine([oof[m] for m in MEMBERS], W)), Y.values).mean())
    print(kind, "OOF TVD (in-sample weights, indicative only):", {k: round(v, 3) for k, v in tv.items()}, flush=True)
    # split-conformal style absolute-residual quantiles from OUT-OF-FOLD stack predictions (global + Mondrian by income group when >=150 rows)
    st_oof = arch.combine([oof[m] for m in MEMBERS], W)
    res = np.abs(st_oof - Y.values)
    def qs(r):
        n = len(r)
        return {str(a): np.quantile(r, min(1.0, (n + 1) * a / n), axis=0).tolist() for a in (0.8, 0.9)}
    conf = {"global": qs(res), "groups": {g: qs(res[(d.income_group == g).values]) for g in d.income_group.unique() if (d.income_group == g).sum() >= 150},
            "min_group_rows": 150, "group_rows": {g: int((d.income_group == g).sum()) for g in d.income_group.unique()},
            "note": "empirical coverage on held-out economies is near nominal overall but BELOW nominal for lower-income groups (results/11_knn_and_conformal/*)"}
    out[key] = {"members": MEMBERS, "components": T, "weights": W.tolist(), "oof_tvd_indicative": tv, "conformal": conf}
json.dump(out, open(pathlib.Path(__file__).resolve().parents[1] / "backend/stack_weights.json", "w"), indent=1)
print("saved")
