"""Robustness: 5 fold-seeds for the headline cold-start comparisons + Holm-Bonferroni; annual-update headline with 5 learner seeds.
Usage: python pipeline/20_robustness_holm.py cold A16|A10 | annual | final
Outputs: results/15_robustness_holm/cold_seeds_<panel>.csv, 15_robustness_holm/rows_<panel>.csv, 15_robustness_holm/annual_rows.csv, 15_robustness_holm/holm.csv, 15_robustness_holm/summary.json
"""
import os
os.environ["OMP_NUM_THREADS"] = "4"
import importlib.util
import json
import sys
import time

import numpy as np
import pandas as pd

HERE = __import__("pathlib").Path(__file__).parent
sys.path.insert(0, str(HERE))
spec = importlib.util.spec_from_file_location("arch03c", HERE / "06_stack_architecture.py")
A = importlib.util.module_from_spec(spec); spec.loader.exec_module(A)
from peer_module import knn_peer_predict

RES, FEATURES, tvd, simplex_renorm = A.RES, A.FEATURES, A.tvd, A.simplex_renorm
SEEDS = [0, 1, 2, 3, 4]
NB = 10000
MEMBERS = ["peer_mean", "ridge", "xgb_clr", "cat_clr"]


def base_preds(Xtr, Ytr, Xte, trm, tem, T, seed, need):
    """Subset of A.cold_fold_preds (identical definitions) computing only what is needed."""
    out = {}
    out["peer_mean"] = np.vstack([trm.groupby("income_group")[T].mean().reindex([g]).fillna(Ytr.mean()).values[0] for g in tem.income_group])
    if "ridge" in need: out["ridge"] = A.fit_predict_multi("ridge", Xtr, Ytr, Xte, seed).values
    if "xgb_raw" in need: out["xgb_raw"] = A.fit_predict_multi("xgb", Xtr, Ytr, Xte, seed).values
    if "xgb_clr" in need or "cat_clr" in need:
        Z = pd.DataFrame(A.clr(Ytr.values), columns=T, index=Ytr.index)
        if "xgb_clr" in need: out["xgb_clr"] = A.inv_clr(A.fit_predict_multi("xgb", Xtr, Z, Xte, seed).values)
        if "cat_clr" in need: out["cat_clr"] = A.inv_clr(A.fit_predict_multi("cat", Xtr, Z, Xte, seed).values)
    return out


def run_cold(kind):
    d, T = A.load_panel(kind)
    d = d.reset_index(drop=True)
    X, Y = d[FEATURES], d[T]
    names = ["peer_mean", "xgb_raw", "cat_clr", "knn8", "STACK"]
    srows, lrows = [], []
    for seed in SEEDS:
        t0 = time.time()
        ctry = d.iso3.unique(); perm = np.random.default_rng(seed).permutation(len(ctry))
        fold = d.iso3.map({c: i % 6 for i, c in zip(range(len(ctry)), ctry[perm])}).values
        oof = {n: np.zeros((len(d), len(T))) for n in names}
        for f in range(6):
            a, b = np.where(fold != f)[0], np.where(fold == f)[0]
            P = base_preds(X.iloc[a], Y.iloc[a], X.iloc[b], d.iloc[a], d.iloc[b], T, 42 + seed, {"ridge", "xgb_raw", "xgb_clr", "cat_clr"})
            P["knn8"] = knn_peer_predict(d.iloc[a], d.iloc[b], T, 8)
            for n in ["peer_mean", "xgb_raw", "cat_clr", "knn8"]: oof[n][b] = P[n]
            ca = d.iloc[a].iso3.unique(); pm = np.random.default_rng(100 + seed + f).permutation(len(ca))
            inner = d.iloc[a].iso3.map({c: i % 4 for i, c in zip(range(len(ca)), ca[pm])}).values
            ioof = {m: np.zeros((len(a), len(T))) for m in MEMBERS}
            for g in range(4):
                ia, ib = np.where(inner != g)[0], np.where(inner == g)[0]
                Pi = base_preds(X.iloc[a].iloc[ia], Y.iloc[a].iloc[ia], X.iloc[a].iloc[ib], d.iloc[a].iloc[ia], d.iloc[a].iloc[ib], T, 7, set(MEMBERS))
                for m in MEMBERS: ioof[m][ib] = Pi[m]
            W = A.nnls_weights([ioof[m] for m in MEMBERS], Y.iloc[a].values)
            oof["STACK"][b] = A.combine([P[m] for m in MEMBERS], W)
        for n in names:
            t = tvd(simplex_renorm(oof[n]), Y.values)
            lo, hi = A.boot_ci(t, d.iso3.values)
            srows.append({"panel": kind, "method": n, "seed": seed, "TVD": float(t.mean()), "TVD_lo": lo, "TVD_hi": hi})
            lrows.append(pd.DataFrame({"panel": kind, "method": n, "seed": seed, "iso3": d.iso3.values, "year": d.year.values, "tvd": t}))
        print(kind, "seed", seed, "done", round(time.time() - t0), "s", flush=True)
        pd.DataFrame(srows).to_csv(RES / f"15_robustness_holm/cold_seeds_{kind}.csv", index=False)
        pd.concat(lrows).to_csv(RES / f"15_robustness_holm/rows_{kind}.csv", index=False)


def run_annual():
    out = []
    for kind in ["A16", "A10"]:
        d, T = A.load_panel(kind)
        ok = d.has_lag
        tr, te = d[ok & (d.year <= 2019)], d[ok & (d.year >= 2020)]
        H = A.hist_feats(T); X2 = FEATURES + H
        L1, L1te = tr[[f"h1_{t}" for t in T]].values, te[[f"h1_{t}" for t in T]].values
        Z = pd.DataFrame(A.clr(tr[T].values) - A.clr(L1), columns=T, index=tr.index)
        out.append(pd.DataFrame({"panel": kind, "method": "persistence", "seed": -1, "iso3": te.iso3.values, "year": te.year.values,
                                 "tvd": tvd(simplex_renorm(L1te), te[T].values)}))
        for s in SEEDS:
            t0 = time.time()
            zx = A.fit_predict_multi("xgb", tr[X2], Z, te[X2], 42 + s).values
            zc = A.fit_predict_multi("cat", tr[X2], Z, te[X2], 42 + s).values
            hy = 0.5 * A.inv_clr(A.clr(L1te) + zx) + 0.5 * A.inv_clr(A.clr(L1te) + zc)
            out.append(pd.DataFrame({"panel": kind, "method": "hybrid_clr_hist", "seed": s, "iso3": te.iso3.values, "year": te.year.values,
                                     "tvd": tvd(simplex_renorm(hy), te[T].values)}))
            print(kind, "annual seed", s, round(time.time() - t0), "s", flush=True)
    pd.concat(out).to_csv(RES / "15_robustness_holm/annual_rows.csv", index=False)


def boot_dist(x, groups, n=NB, seed=0):
    rng = np.random.default_rng(seed)
    g = pd.Series(np.asarray(x, float)).groupby(np.asarray(groups)).agg(["sum", "count"])
    ids = rng.integers(0, len(g), (n, len(g)))
    return g["sum"].values[ids].sum(1) / g["count"].values[ids].sum(1)


def summ(gain, groups):
    m = boot_dist(gain, groups)
    p = min(1.0, 2 * min((m <= 0).mean(), (m >= 0).mean()))
    p = max(p, 1.0 / (len(m) + 1))
    return {"gain": float(np.mean(gain)), "lo": float(np.percentile(m, 2.5)), "hi": float(np.percentile(m, 97.5)), "p_boot": float(p)}


def holm(ps):
    ps = np.asarray(ps); o = np.argsort(ps); m = len(ps); adj = np.zeros(m); run = 0
    for r, i in enumerate(o):
        run = max(run, (m - r) * ps[i]); adj[i] = min(1.0, run)
    return adj


def final():
    rows, summary = [], {"note": "TVD per seed then averaged; bootstrap = cluster (iso3) resampling, 10000 reps; p=2*min(P(g<=0),P(g>=0)) floored at 1/10001."}
    cold_means = []
    for kind in ["A16", "A10"]:
        L = pd.read_csv(RES / f"15_robustness_holm/rows_{kind}.csv")
        W = L.pivot_table(index=["iso3", "year", "seed"], columns="method", values="tvd").reset_index()
        seeds = sorted(W.seed.unique())
        S = pd.read_csv(RES / f"15_robustness_holm/cold_seeds_{kind}.csv")
        for n in ["peer_mean", "xgb_raw", "cat_clr", "knn8", "STACK"]:
            per = S[S.method == n].TVD.values
            avg = W.groupby(["iso3", "year"])[n].mean().reset_index()
            lo, hi = A.boot_ci(avg[n].values, avg.iso3.values)
            cold_means.append({"panel": kind, "method": n, "TVD_mean_over_seeds": float(per.mean()), "sd_over_seeds": float(per.std(ddof=1)),
                               "ci95_lo": lo, "ci95_hi": hi, "per_seed": [round(float(x), 4) for x in per], "n_seeds": len(per)})
        comps = [("STACK", "peer_mean"), ("xgb_raw", "peer_mean"), ("knn8", "peer_mean"), ("cat_clr", "peer_mean"), ("STACK", "xgb_raw")]
        for a, b in comps:
            head = (a, b) != ("cat_clr", "peer_mean")
            g_seed = []
            for s in seeds:
                w = W[W.seed == s]; r = summ((w[b] - w[a]).values, w.iso3.values); r["seed"] = int(s); g_seed.append(r)
            avgW = W.groupby(["iso3", "year"])[[a, b]].mean().reset_index()
            r = summ((avgW[b] - avgW[a]).values, avgW.iso3.values)
            rows.append({"family": "cold_start_headline" if head else "cold_start_extra", "panel": kind, "comparison": f"{a} vs {b}", "gain_pp_mean_over_seeds": r["gain"],
                         "ci95_lo": r["lo"], "ci95_hi": r["hi"], "p_boot": r["p_boot"],
                         "per_seed_gain": [round(x["gain"], 4) for x in g_seed], "per_seed_p": [round(x["p_boot"], 4) for x in g_seed],
                         "seeds_gain_positive": int(sum(x["gain"] > 0 for x in g_seed))})
    # annual
    An = pd.read_csv(RES / "15_robustness_holm/annual_rows.csv")
    ann_summary = {}
    for kind in ["A16", "A10"]:
        a = An[An.panel == kind]
        pers = a[a.method == "persistence"].set_index(["iso3", "year"]).tvd
        hy = a[a.method == "hybrid_clr_hist"].pivot_table(index=["iso3", "year"], columns="seed", values="tvd")
        per_seed = hy.mean(0).values
        avg = hy.mean(1)
        gain = (pers.reindex(avg.index) - avg)
        r = summ(gain.values, gain.index.get_level_values(0).values)
        gseeds = [float((pers.reindex(hy.index) - hy[s]).mean()) for s in hy.columns]
        lo, hi = A.boot_ci(avg.values, avg.index.get_level_values(0).values)
        ann_summary[kind] = {"persistence_TVD": float(pers.mean()), "hybrid_TVD_mean": float(per_seed.mean()), "hybrid_TVD_sd": float(per_seed.std(ddof=1)),
                             "hybrid_ci95": [lo, hi], "per_seed_TVD": [round(float(x), 4) for x in per_seed], "per_seed_gain": [round(x, 4) for x in gseeds], "n_rows": int(len(avg))}
        rows.append({"family": "annual_headline", "panel": kind, "comparison": "hybrid_clr_hist vs persistence", "gain_pp_mean_over_seeds": r["gain"], "ci95_lo": r["lo"], "ci95_hi": r["hi"],
                     "p_boot": r["p_boot"], "per_seed_gain": [round(x, 4) for x in gseeds], "per_seed_p": [], "seeds_gain_positive": int(sum(x > 0 for x in gseeds))})
    R = pd.DataFrame(rows)
    R["p_holm_within_family"] = np.nan; R["p_holm_all_headline"] = np.nan
    for fam in ["cold_start_headline", "annual_headline"]:
        m = R.family == fam
        R.loc[m, "p_holm_within_family"] = holm(R.loc[m, "p_boot"].values)
    m = R.family.isin(["cold_start_headline", "annual_headline"])
    R.loc[m, "p_holm_all_headline"] = holm(R.loc[m, "p_boot"].values)
    R["survives_holm_0.05_family"] = R.p_holm_within_family < 0.05
    R["survives_holm_0.05_all"] = R.p_holm_all_headline < 0.05
    R.to_csv(RES / "15_robustness_holm/holm.csv", index=False)
    summary["cold_means"] = cold_means; summary["annual"] = ann_summary
    summary["holm"] = json.loads(R.to_json(orient="records"))
    json.dump(summary, open(RES / "15_robustness_holm/summary.json", "w"), indent=1)
    pd.set_option("display.width", 250)
    print(pd.DataFrame(cold_means).drop(columns="per_seed").round(3).to_string())
    print(R.drop(columns=["per_seed_p"]).round(4).to_string())
    print(json.dumps(ann_summary, indent=1))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "cold": run_cold(sys.argv[2])
    elif cmd == "annual": run_annual()
    else: final()
