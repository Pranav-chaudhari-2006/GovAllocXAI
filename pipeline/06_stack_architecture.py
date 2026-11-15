"""Architecture v2.1 ("Stack"): history features + compositional (CLR) targets + NNLS stacking, evaluated honestly.

Panels   : A16 (16 COFOG functions + residual; Eurostat+OECD) and A10 (10 COFOG divisions; Eurostat+OECD+IMF, incl. non-OECD).
Regime H : one-step-ahead with history.  Weights of the stacked ensemble are fitted on a VALIDATION window (train<=2016 -> val 2017-19);
           base models are then refit on <=2019 and evaluated ONCE on 2020-24.
Regime C : cold start, leave-country-out (6 folds x 2 seeds); stack weights fitted by NESTED inner grouped CV inside every outer training fold.
Outputs  : results/04_stack_architecture/<panel>_history.csv, 04_stack_architecture/<panel>_cold.csv, 04_stack_architecture/summary.json
Usage    : python pipeline/06_stack_architecture.py [A16|A10|both]
"""
import json
import sys

import numpy as np
import pandas as pd
from scipy.optimize import nnls

sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from gov_common import *  # noqa: F401,F403

EPS = 0.05


def clr(Y):
    L = np.log(np.clip(np.asarray(Y, float), 0, None) + EPS)   # residual component can be slightly negative -> clip
    return L - L.mean(1, keepdims=True)


def inv_clr(Z, total=100.0):
    E = np.exp(Z - Z.max(1, keepdims=True))
    return E / E.sum(1, keepdims=True) * total


def load_panel(kind):
    if kind == "A16":
        d = load_cofog(); T = TARGETS_A
    else:
        d = pd.read_csv(PROC / "govalloc_cofog_panel_a10.csv").sort_values(["iso3", "year"]).reset_index(drop=True)
        T = [f"cofog10_GF{i:02d}_pct_total" for i in range(1, 11)]
    g = d.groupby("iso3")
    new = {}
    for t in T:
        y1 = g[t].shift(1); y2 = g[t].shift(2)
        ok1 = (d.year - g["year"].shift(1)) == 1
        ok2 = (d.year - g["year"].shift(2)) == 2
        new[f"h1_{t}"] = y1.where(ok1)
        new[f"h2_{t}"] = y2.where(ok2)
        new[f"hT_{t}"] = (new[f"h1_{t}"] - new[f"h2_{t}"])
        # expanding country mean of PAST values only (shifted), and mean of last three observed past values
        new[f"hM_{t}"] = g[t].transform(lambda s: s.shift(1).expanding().mean())
    N = pd.DataFrame(new)
    d = pd.concat([d.drop(columns=[c for c in N.columns if c in d.columns]), N], axis=1)
    d["has_lag"] = d[[f"h1_{t}" for t in T]].notna().all(axis=1)
    return d, T


def hist_feats(T):
    return [f"{p}_{t}" for p in ("h1", "h2", "hT", "hM") for t in T]


def nnls_weights(preds, y):
    """preds: list of (n, K) arrays; y: (n, K). Per-component non-negative weights summing to 1. Returns (M, K)."""
    M, K = len(preds), y.shape[1]
    W = np.zeros((M, K))
    for k in range(K):
        A = np.column_stack([p[:, k] for p in preds])
        w, _ = nnls(A, y[:, k])
        W[:, k] = w / w.sum() if w.sum() > 0 else 1.0 / M
    return W


def combine(preds, W):
    return sum(p * W[i][None, :] for i, p in enumerate(preds))


def tvd_boot(P, A, groups):
    t = tvd(simplex_renorm(P), A)
    lo, hi = boot_ci(t, groups)
    return float(t.mean()), lo, hi, t


# ------------------------------------------------------------------ regime H
def history_preds(d, T, tr, te, base_feats):
    """Return dict name -> predictions (n_te, K) for all candidate models trained on tr, applied to te."""
    H = hist_feats(T)
    L1 = tr[[f"h1_{t}" for t in T]].values; L1te = te[[f"h1_{t}" for t in T]].values
    out = {"persistence": L1te}
    cm = te[[f"hM_{t}" for t in T]].fillna(pd.DataFrame(np.tile(tr[T].mean().values, (len(te), 1)), index=te.index, columns=[f"hM_{t}" for t in T])).values
    out["country_mean_past"] = cm
    # (a) raw delta, base features + lag1 only (= v2 architecture)
    X1 = base_feats + [f"h1_{t}" for t in T]
    D = fit_predict_multi("xgb", tr[X1], pd.DataFrame(tr[T].values - L1, columns=T, index=tr.index), te[X1]).values
    out["delta_xgb_v2"] = L1te + D
    # (b) raw delta with richer history
    X2 = base_feats + H
    D2 = fit_predict_multi("xgb", tr[X2], pd.DataFrame(tr[T].values - L1, columns=T, index=tr.index), te[X2]).values
    out["delta_xgb_hist"] = L1te + D2
    Dc = fit_predict_multi("cat", tr[X2], pd.DataFrame(tr[T].values - L1, columns=T, index=tr.index), te[X2]).values
    out["delta_cat_hist"] = L1te + Dc
    # (c) delta in CLR space, richer history
    Z = pd.DataFrame(clr(tr[T].values) - clr(L1), columns=T, index=tr.index)
    Zh = fit_predict_multi("xgb", tr[X2], Z, te[X2]).values
    out["delta_clr_xgb_hist"] = inv_clr(clr(L1te) + Zh)
    Zc = fit_predict_multi("cat", tr[X2], Z, te[X2]).values
    out["delta_clr_cat_hist"] = inv_clr(clr(L1te) + Zc)
    out["hybrid_clr_hist"] = 0.5 * out["delta_clr_xgb_hist"] + 0.5 * out["delta_clr_cat_hist"]
    return out


def run_history(kind):
    d, T = load_panel(kind)
    bf = FEATURES
    ok = d.has_lag
    tr_v, va = d[ok & (d.year <= 2016)], d[ok & (d.year >= 2017) & (d.year <= 2019)]
    tr_t, te = d[ok & (d.year <= 2019)], d[ok & (d.year >= 2020)]
    print(kind, "history: train_val", len(tr_v), "val", len(va), "train_test", len(tr_t), "test", len(te), "test economies", te.iso3.nunique(), flush=True)
    pv = history_preds(d, T, tr_v, va, bf)
    pt = history_preds(d, T, tr_t, te, bf)
    names = list(pt)
    rows = []
    for n in names:
        mv, lov, hiv, _ = tvd_boot(pv[n], va[T].values, va.iso3.values)
        mt, lot, hit, tt = tvd_boot(pt[n], te[T].values, te.iso3.values)
        rows.append({"method": n, "TVD_val": mv, "TVD_test": mt, "TVD_test_lo": lot, "TVD_test_hi": hit, "n_test": len(te)})
    # stack: weights fitted on validation predictions (non-negative, sum 1, per component)
    stack_members = ["persistence", "country_mean_past", "delta_xgb_hist", "delta_clr_xgb_hist", "delta_clr_cat_hist"]
    W = nnls_weights([pv[m] for m in stack_members], va[T].values)
    Pst_v, Pst_t = combine([pv[m] for m in stack_members], W), combine([pt[m] for m in stack_members], W)
    mv, *_ = tvd_boot(Pst_v, va[T].values, va.iso3.values)
    mt, lot, hit, tt_stack = tvd_boot(Pst_t, te[T].values, te.iso3.values)
    rows.append({"method": "STACK v2.1 (NNLS on validation)", "TVD_val": mv, "TVD_test": mt, "TVD_test_lo": lot, "TVD_test_hi": hit, "n_test": len(te)})
    R = pd.DataFrame(rows); R.to_csv(RES / f"04_stack_architecture/{kind}_history.csv", index=False)
    print(R.round(3).to_string(), flush=True)
    base_t = tvd(simplex_renorm(pt["persistence"]), te[T].values)
    base_v2 = tvd(simplex_renorm(pt["delta_xgb_v2"]), te[T].values)
    paired = {}
    for name, tt in [("STACK_vs_persistence", base_t - tt_stack), ("STACK_vs_v2_delta_xgb", base_v2 - tt_stack)]:
        lo, hi = boot_ci(tt, te.iso3.values)
        paired[name] = {"mean_gain_pp": float(tt.mean()), "ci95": [lo, hi], "share_rows_improved": float((tt > 0).mean())}
    pd.DataFrame(W, index=stack_members, columns=[c.replace("cofog_", "").replace("cofog10_", "").replace("_pct_total", "") for c in T]).to_csv(RES / f"04_stack_architecture/{kind}_stack_weights.csv")
    # allocation engine (default bounds) on the stack
    lo_b, hi_b = tr_t[T].min().values * 0.5, tr_t[T].max().values * 1.5
    Pal = allocate(simplex_renorm(Pst_t), lo_b, hi_b)
    paired["stack_TVD_after_engine"] = float(tvd(Pal, te[T].values).mean())
    return {"rows": R.to_dict("records"), "paired": paired, "n_test": len(te), "n_test_economies": int(te.iso3.nunique()),
            "n_train": len(tr_t), "weights_mean": dict(zip(stack_members, W.mean(1).round(3)))}


# ------------------------------------------------------------------ regime C
def cold_fold_preds(Xtr, Ytr, Xte, tr_meta, te_meta, T, seed=42):
    out = {}
    out["peer_mean"] = np.vstack([tr_meta.groupby("income_group")[T].mean().reindex([g]).fillna(Ytr.mean()).values[0] if True else 0 for g in te_meta.income_group])
    out["ridge"] = fit_predict_multi("ridge", Xtr, Ytr, Xte, seed).values
    out["xgb_raw"] = fit_predict_multi("xgb", Xtr, Ytr, Xte, seed).values
    Z = pd.DataFrame(clr(Ytr.values), columns=T, index=Ytr.index)
    out["xgb_clr"] = inv_clr(fit_predict_multi("xgb", Xtr, Z, Xte, seed).values)
    out["cat_clr"] = inv_clr(fit_predict_multi("cat", Xtr, Z, Xte, seed).values)
    out["hybrid_clr"] = 0.5 * out["xgb_clr"] + 0.5 * out["cat_clr"]
    return out


def run_cold(kind):
    d, T = load_panel(kind)
    X, Y = d[FEATURES], d[T]
    d = d.reset_index(drop=True)
    names = ["peer_mean", "ridge", "xgb_raw", "xgb_clr", "cat_clr", "hybrid_clr", "STACK v2.1 (nested NNLS)"]
    rows, keep = [], {}
    for seed in [0, 1]:
        ctry = d.iso3.unique(); perm = np.random.default_rng(seed).permutation(len(ctry))
        fold = d.iso3.map({c: i % 6 for i, c in zip(range(len(ctry)), ctry[perm])}).values
        oof = {n: np.zeros((len(d), len(T))) for n in names}
        for f in range(6):
            a, b = np.where(fold != f)[0], np.where(fold == f)[0]
            P = cold_fold_preds(X.iloc[a], Y.iloc[a], X.iloc[b], d.iloc[a], d.iloc[b], T, 42 + seed)
            for n in P: oof[n][b] = P[n]
            # nested inner grouped CV to obtain OOF base predictions on the training countries -> NNLS weights
            ca = d.iloc[a].iso3.unique(); pm = np.random.default_rng(100 + seed + f).permutation(len(ca))
            inner = d.iloc[a].iso3.map({c: i % 4 for i, c in zip(range(len(ca)), ca[pm])}).values
            members = ["peer_mean", "ridge", "xgb_clr", "cat_clr"]
            inner_oof = {m: np.zeros((len(a), len(T))) for m in members}
            for g in range(4):
                ia, ib = np.where(inner != g)[0], np.where(inner == g)[0]
                Pi = cold_fold_preds(X.iloc[a].iloc[ia], Y.iloc[a].iloc[ia], X.iloc[a].iloc[ib], d.iloc[a].iloc[ia], d.iloc[a].iloc[ib], T, 7)
                for m in members: inner_oof[m][ib] = Pi[m]
            W = nnls_weights([inner_oof[m] for m in members], Y.iloc[a].values)
            oof["STACK v2.1 (nested NNLS)"][b] = combine([P[m] for m in members], W)
        for n in names:
            m_, lo, hi, t = tvd_boot(oof[n], Y.values, d.iso3.values)
            rows.append({"method": n, "seed": seed, "TVD": m_, "TVD_lo": lo, "TVD_hi": hi, "MAE_pp": float(np.abs(simplex_renorm(oof[n]) - Y.values).mean())})
            if seed == 0: keep[n] = t
        print(kind, "cold seed", seed, "done", flush=True)
    R = pd.DataFrame(rows).groupby("method").mean(numeric_only=True).reset_index().drop(columns="seed").sort_values("TVD")
    R.to_csv(RES / f"04_stack_architecture/{kind}_cold.csv", index=False); print(R.round(3).to_string(), flush=True)
    paired = {}
    for n in ["xgb_raw", "STACK v2.1 (nested NNLS)"]:
        dd = keep["peer_mean"] - keep[n]; lo, hi = boot_ci(dd, d.iso3.values)
        paired[f"{n}_vs_peer_mean"] = {"mean_gain_pp": float(dd.mean()), "ci95": [lo, hi]}
    return {"rows": R.to_dict("records"), "paired": paired, "n": len(d), "n_economies": int(d.iso3.nunique())}


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    out = {}
    for kind in (["A16", "A10"] if which == "both" else [which]):
        out[kind] = {"history": run_history(kind), "cold": run_cold(kind)}
    fn = RES / "04_stack_architecture/summary.json"
    old = json.load(open(fn)) if fn.exists() else {}
    old.update(out)
    json.dump(old, open(fn, "w"), indent=1, default=float)
    print("done")
