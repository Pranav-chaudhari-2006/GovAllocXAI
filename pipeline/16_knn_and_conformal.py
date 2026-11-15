"""Exp K: (1) KNN similar-countries predictor, cold-start, alone and as an extra member of the nested-NNLS stack;
(2) group-aware split-conformal (and income-group Mondrian) intervals for cold-start composition predictions.
Cold start = leave-country-out, 6 folds, seed 0 (same fold construction as 03c). Panels A16 and A10.
Outputs: results/11_knn_and_conformal/<panel>_knn.csv, 11_knn_and_conformal/<panel>_conformal.csv, 11_knn_and_conformal/<panel>_conformal_by_group.csv, 11_knn_and_conformal/summary.json
Usage: python pipeline/16_knn_and_conformal.py [A16|A10|both]
"""
import os
os.environ["OMP_NUM_THREADS"] = "4"
import tempfile
os.chdir(tempfile.gettempdir())   # catboost writes catboost_info into cwd; keep it out of the repo / unwritable dirs
import importlib.util
import json
import math
import pathlib
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from gov_common import *  # noqa: F401,F403
from peer_module import knn_peer_predict

_spec = importlib.util.spec_from_file_location("arch03c", str(pathlib.Path(__file__).parent / "06_stack_architecture.py"))
A = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(A)

import gov_common as _gc
_orig_make = _gc.make_model


def _fast_make(name, seed=42):
    """Same hyper-parameters as gov_common.make_model but single-threaded (multi-threading is slower on this small data under shared CPU)."""
    m = _orig_make(name, seed)
    if name == "xgb":
        m.set_params(n_jobs=1)
    elif name == "cat":
        m.set_params(thread_count=1)
    return m


_gc.make_model = _fast_make

KS = [3, 5, 8, 12]
ALPHAS = [0.2, 0.1]
MIN_ROWS_MONDRIAN, MIN_ECON_MONDRIAN = 150, 6


def qhat(res, alpha):
    """Finite-sample split-conformal quantile of absolute residuals (1-D)."""
    n = len(res)
    lev = min(1.0, math.ceil((n + 1) * (1 - alpha)) / n)
    return float(np.quantile(res, lev, method="higher"))


def conformal_q(res, groups, econ, te_groups, alpha, mondrian):
    """res (n_cal, K) abs residuals; returns q matrix (n_te, K)."""
    K = res.shape[1]
    qg = np.array([qhat(res[:, k], alpha) for k in range(K)])
    Q = np.tile(qg, (len(te_groups), 1))
    if mondrian:
        for g in np.unique(te_groups):
            m = groups == g
            if m.sum() >= MIN_ROWS_MONDRIAN and len(np.unique(econ[m])) >= MIN_ECON_MONDRIAN:
                qq = np.array([qhat(res[m, k], alpha) for k in range(K)])
                Q[te_groups == g] = qq
    return Q


def setup(kind):
    d, T = A.load_panel(kind)
    d = d.reset_index(drop=True)
    ctry = d.iso3.unique(); perm = np.random.default_rng(0).permutation(len(ctry))
    fold = d.iso3.map({c: i % 6 for i, c in zip(range(len(ctry)), ctry[perm])}).values
    return d, T, fold


def fold_job(kind, f):
    d, T, fold = setup(kind)
    X, Y = d[FEATURES], d[T]
    K = len(T)
    base_m = ["peer_mean", "ridge", "xgb_clr", "cat_clr"]
    cmethods = ["xgb_raw", "knn5", "STACK_base"]
    a, b = np.where(fold != f)[0], np.where(fold == f)[0]
    tr, te = d.iloc[a], d.iloc[b]
    P = A.cold_fold_preds(X.iloc[a], Y.iloc[a], X.iloc[b], tr, te, T, 42)
    for k in KS:
        P[f"knn{k}"] = knn_peer_predict(tr, te, T, k)
    ca = tr.iso3.unique(); pm = np.random.default_rng(100 + f).permutation(len(ca))
    inner = tr.iso3.map({c: i % 4 for i, c in zip(range(len(ca)), ca[pm])}).values
    mem_all = ["peer_mean", "ridge", "xgb_raw", "xgb_clr", "cat_clr"] + [f"knn{k}" for k in KS]
    ioof = {m: np.zeros((len(a), K)) for m in mem_all}
    for g in range(4):
        ia, ib = np.where(inner != g)[0], np.where(inner == g)[0]
        Pi = A.cold_fold_preds(X.iloc[a].iloc[ia], Y.iloc[a].iloc[ia], X.iloc[a].iloc[ib], tr.iloc[ia], tr.iloc[ib], T, 7)
        for m in ["peer_mean", "ridge", "xgb_raw", "xgb_clr", "cat_clr"]:
            ioof[m][ib] = Pi[m]
        for k in KS:
            ioof[f"knn{k}"][ib] = knn_peer_predict(tr.iloc[ia], tr.iloc[ib], T, k)
    ytr = Y.iloc[a].values
    out = {"b": b, "oof": {}, "ci": {}}
    for m in ["peer_mean", "ridge", "xgb_raw", "xgb_clr", "cat_clr"] + [f"knn{k}" for k in KS]:
        out["oof"][m] = P[m]
    W = A.nnls_weights([ioof[m] for m in base_m], ytr)
    out["oof"]["STACK_base"] = A.combine([P[m] for m in base_m], W)
    ioof["STACK_base"] = A.combine([ioof[m] for m in base_m], W)
    P["STACK_base"] = out["oof"]["STACK_base"]
    for k in KS:
        mm = base_m + [f"knn{k}"]
        Wk = A.nnls_weights([ioof[m] for m in mm], ytr)
        out["oof"][f"STACK_base+knn{k}"] = A.combine([P[m] for m in mm], Wk)
    # conformal: calibrate on inner OOF residuals of TRAINING economies only
    for m in cmethods:
        res = np.abs(simplex_renorm(ioof[m]) - ytr)
        pt = simplex_renorm(P[m])
        for al in ALPHAS:
            for v in ("global", "mondrian"):
                Q = conformal_q(res, tr.income_group.values, tr.iso3.values, te.income_group.values, al, v == "mondrian")
                out["ci"][(m, al, v)] = (pt - Q, pt + Q)
    print(kind, "fold", f, "done", flush=True)
    return out


def run(kind):
    from concurrent.futures import ProcessPoolExecutor
    d, T, fold = setup(kind)
    Y = d[T]
    K = len(T)
    stacks = ["STACK_base"] + [f"STACK_base+knn{k}" for k in KS]
    names = ["peer_mean", "ridge", "xgb_raw", "xgb_clr", "cat_clr"] + [f"knn{k}" for k in KS] + stacks
    cmethods = ["xgb_raw", "knn5", "STACK_base"]
    oof = {n: np.zeros((len(d), K)) for n in names}
    lo_hi = {(m, a, v): [np.zeros((len(d), K)), np.zeros((len(d), K))] for m in cmethods for a in ALPHAS for v in ("global", "mondrian")}
    with ProcessPoolExecutor(max_workers=3) as ex:
        results = list(ex.map(fold_job, [kind] * 6, range(6)))
    for r in results:
        b = r["b"]
        for n in names:
            oof[n][b] = r["oof"][n]
        for key, (lo, hi) in r["ci"].items():
            lo_hi[key][0][b] = lo; lo_hi[key][1][b] = hi

    # ------------- KNN / stack evaluation
    t = {n: tvd(simplex_renorm(oof[n]), Y.values) for n in names}
    rows = []
    for n in names:
        lo, hi = boot_ci(t[n], d.iso3.values)
        rows.append({"method": n, "TVD": float(t[n].mean()), "TVD_lo": lo, "TVD_hi": hi})
    R = pd.DataFrame(rows)
    # paired gains (positive = first method better)
    pairs = [(f"knn{k}", "peer_mean") for k in KS] + [(f"knn{k}", "xgb_raw") for k in KS] + \
            [(f"STACK_base+knn{k}", "STACK_base") for k in KS] + [("STACK_base", "peer_mean"), ("xgb_raw", "peer_mean")]
    paired = {}
    for m1, m2 in pairs:
        dd = t[m2] - t[m1]
        lo, hi = boot_ci(dd, d.iso3.values)
        paired[f"{m1}_vs_{m2}"] = {"mean_gain_pp": float(dd.mean()), "ci95": [lo, hi]}
    R.to_csv(RES / f"11_knn_and_conformal/{kind}_knn.csv", index=False)
    print(R.round(3).to_string(), flush=True)
    for k_, v_ in paired.items():
        print(" ", k_, round(v_["mean_gain_pp"], 3), [round(x, 3) for x in v_["ci95"]])

    # ------------- conformal evaluation
    crow, grow = [], []
    Yv = Y.values
    for (m, al, v), (lo, hi) in lo_hi.items():
        cov = ((Yv >= lo) & (Yv <= hi))
        wid = hi - lo
        crow.append({"method": m, "alpha": al, "variant": v, "nominal": 1 - al, "coverage": float(cov.mean()),
                     "coverage_econ_avg": float(pd.Series(cov.mean(1)).groupby(d.iso3.values).mean().mean()),
                     "mean_width_pp": float(wid.mean())})
        for g in d.income_group.unique():
            mk = (d.income_group == g).values
            grow.append({"method": m, "alpha": al, "variant": v, "income_group": g, "economies": int(d.iso3[mk].nunique()),
                         "rows": int(mk.sum()), "coverage": float(cov[mk].mean()), "mean_width_pp": float(wid[mk].mean())})
        if m == "xgb_raw" and v == "global" and al == 0.1:
            pd.DataFrame(cov.mean(0), index=T, columns=["coverage"]).to_csv(RES / f"11_knn_and_conformal/{kind}_coverage_by_component_xgb_a0.1.csv")
    C, G = pd.DataFrame(crow), pd.DataFrame(grow)
    C.to_csv(RES / f"11_knn_and_conformal/{kind}_conformal.csv", index=False); G.to_csv(RES / f"11_knn_and_conformal/{kind}_conformal_by_group.csv", index=False)
    print(C.round(3).to_string()); print(G[G.method == "xgb_raw"].round(3).to_string(), flush=True)
    return {"knn_rows": R.to_dict("records"), "paired": paired, "conformal": C.to_dict("records"),
            "conformal_by_group": G.to_dict("records"), "n": len(d), "economies": int(d.iso3.nunique()),
            "note": "seed 0, 6 outer folds, 4 inner folds; calibration = inner OOF residuals on training economies only"}


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    out = {}
    for kind in (["A16", "A10"] if which == "both" else [which]):
        out[kind] = run(kind)
    fn = RES / "11_knn_and_conformal/summary.json"
    old = json.load(open(fn)) if fn.exists() else {}
    old.update(out)
    json.dump(old, open(fn, "w"), indent=1, default=float)
    print("done")
