"""Explain the production STACK (not just its XGBoost member) with KernelSHAP + synthetic ground-truth sanity test for SHAP/LIME.
Task A: panel A10, hold out 20% of economies; members peer_mean, ridge, xgb_clr, cat_clr fitted on the rest; blend weights from backend/stack_weights.json
        (weights come from out-of-fold fits on all data: indicative). KernelSHAP of the blend vs TreeSHAP of the raw XGBoost member for 3 divisions.
Task B: synthetic data with KNOWN drivers: precision@3 / rank correlation of TreeSHAP and LIME, with and without a correlated copy of a driver.
Outputs results/17_blend_explanation/blend.csv, 17_blend_explanation/sanity.csv, 17_blend_explanation/summary.json
"""
import importlib.util
import json
import os
import pathlib
import sys

os.environ.setdefault("OMP_NUM_THREADS", "4")
import numpy as np
import pandas as pd
import shap
from lime.lime_tabular import LimeTabularExplainer
from scipy.stats import spearmanr
from xgboost import XGBRegressor

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
from gov_common import *  # noqa: F401,F403

spec = importlib.util.spec_from_file_location("arch21", HERE / "06_stack_architecture.py")
arch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(arch)
rng = np.random.default_rng(0)
summary = {}

# ----------------------------------------------------------------------------- Task A
d, T = arch.load_panel("A10")
d = d.reset_index(drop=True)
ctry = d.iso3.unique()
hold = set(rng.choice(ctry, size=max(8, len(ctry) // 5), replace=False))
tr, te = d[~d.iso3.isin(hold)], d[d.iso3.isin(hold)]
Xtr, Ytr = tr[FEATURES].values.astype(float), tr[T].values.astype(float)
med = np.nanmedian(Xtr, 0)
fill = lambda X: np.where(np.isnan(X), med, X)
Xtr_f = fill(Xtr)
W = np.array(json.load(open(HERE.parent / "backend/stack_weights.json"))["cofog10"]["weights"])
mu, sd = Ytr.mean(0), Ytr.std(0)
from catboost import CatBoostRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

Z = arch.clr(Ytr)
zmu, zsd = Z.mean(0), Z.std(0)
ridge = [make_pipeline(StandardScaler(), Ridge(alpha=10.0)).fit(Xtr_f, (Ytr[:, j] - mu[j]) / sd[j]) for j in range(len(T))]
xgbc = [XGBRegressor(n_estimators=300, learning_rate=0.05, max_depth=3, subsample=0.8, colsample_bytree=0.8, min_child_weight=3, reg_lambda=5.0, random_state=42, n_jobs=4, verbosity=0).fit(Xtr_f, (Z[:, j] - zmu[j]) / zsd[j]) for j in range(len(T))]
catc = [CatBoostRegressor(iterations=300, learning_rate=0.07, depth=4, l2_leaf_reg=5.0, random_seed=42, verbose=0, thread_count=4).fit(Xtr_f, (Z[:, j] - zmu[j]) / zsd[j]) for j in range(len(T))]
xgb_raw = [XGBRegressor(n_estimators=300, learning_rate=0.05, max_depth=3, subsample=0.8, colsample_bytree=0.8, min_child_weight=3, reg_lambda=5.0, random_state=42, n_jobs=4, verbosity=0).fit(Xtr_f, Ytr[:, j]) for j in range(len(T))]
gmean = tr.groupby("income_group")[T].mean()


def blend_all(X, grp):
    X = np.atleast_2d(X)
    peer = np.tile((gmean.loc[grp].values if grp in gmean.index else Ytr.mean(0)), (len(X), 1))
    r = np.column_stack([m.predict(X) for m in ridge]) * sd + mu
    zx = np.column_stack([m.predict(X) for m in xgbc]) * zsd + zmu
    zc = np.column_stack([m.predict(X) for m in catc]) * zsd + zmu
    preds = [peer, r, arch.inv_clr(zx), arch.inv_clr(zc)]
    return sum(p * W[i][None, :] for i, p in enumerate(preds))


rows = []
sample = te.sample(n=min(30, len(te)), random_state=0)
bg = shap.kmeans(Xtr_f, 30)
for j, dv in [(T.index("cofog10_GF07_pct_total"), "GF07 health"), (T.index("cofog10_GF09_pct_total"), "GF09 education"), (T.index("cofog10_GF10_pct_total"), "GF10 social protection")]:
    tree = shap.TreeExplainer(xgb_raw[j])
    rho, jac, sgn, fa_k, fa_r = [], [], [], [], []
    for _, r_ in sample.iterrows():
        x = fill(r_[FEATURES].values.astype(float)[None, :])
        grp = r_["income_group"]
        f = lambda A, grp=grp, j=j: blend_all(A, grp)[:, j]
        ks = shap.KernelExplainer(f, bg).shap_values(x, nsamples=200, silent=True)[0]
        ts = tree.shap_values(x)[0]
        rho.append(spearmanr(np.abs(ks), np.abs(ts))[0])
        a, b = set(np.argsort(-np.abs(ks))[:5]), set(np.argsort(-np.abs(ts))[:5])
        jac.append(len(a & b) / len(a | b))
        top = np.argsort(-np.abs(ks))[:5]
        sgn.append(float(np.mean(np.sign(ks[top]) == np.sign(ts[top]))))
        base = f(x)[0]
        xk, xr = x.copy(), x.copy()
        xk[0, np.argsort(-np.abs(ks))[:3]] = Xtr_f.mean(0)[np.argsort(-np.abs(ks))[:3]]
        ri = rng.choice(len(FEATURES), 3, replace=False)
        xr[0, ri] = Xtr_f.mean(0)[ri]
        fa_k.append(abs(f(xk)[0] - base)); fa_r.append(abs(f(xr)[0] - base))
    rows.append({"division": dv, "n_rows": len(sample), "spearman_blend_vs_xgb_member": float(np.nanmean(rho)), "top5_jaccard": float(np.mean(jac)), "top5_sign_agreement": float(np.mean(sgn)),
                 "faithfulness_ratio_kernelshap_on_blend": float(np.mean(fa_k) / max(np.mean(fa_r), 1e-9))})
    print(rows[-1], flush=True)
pd.DataFrame(rows).to_csv(RES / "17_blend_explanation/blend.csv", index=False)
summary["blend"] = rows

# ----------------------------------------------------------------------------- Task B
Xall = d[FEATURES].values.astype(float)
Xall = np.where(np.isnan(Xall), np.nanmedian(Xall, 0), Xall)
Xz = (Xall - Xall.mean(0)) / np.where(Xall.std(0) == 0, 1, Xall.std(0))
A_, B_, C_ = FEATURES.index("log_gdp"), FEATURES.index("pop_65plus_pct"), FEATURES.index("urban_pop_pct")
res = []
for variant in ["independent", "correlated_copy"]:
    for rep in range(20):
        r2 = np.random.default_rng(100 + rep)
        idx = r2.integers(0, len(Xz), 600)
        X = Xz[idx].copy()
        if variant == "correlated_copy":
            X[:, FEATURES.index("tax_revenue_pct_gdp")] = X[:, A_] + 0.15 * r2.normal(size=len(X))   # near-copy of driver A
        y = 4 * X[:, A_] + 2 * X[:, B_] * X[:, C_] + 0.3 * r2.normal(size=len(X))
        m = XGBRegressor(n_estimators=250, learning_rate=0.05, max_depth=3, subsample=0.8, random_state=rep, n_jobs=4, verbosity=0).fit(X[:500], y[:500])
        Xt = X[500:]
        sv = shap.TreeExplainer(m).shap_values(Xt)
        shap_imp = np.abs(sv).mean(0)
        ex = LimeTabularExplainer(X[:500], feature_names=FEATURES, mode="regression", discretize_continuous=False, random_state=rep)
        li = np.zeros(len(FEATURES))
        for i in range(30):
            e = ex.explain_instance(Xt[i], m.predict, num_features=len(FEATURES), num_samples=800)
            for k, v in e.local_exp[list(e.local_exp)[0]]:
                li[k] += abs(v)
        truth = {A_, B_, C_}
        for name, imp in [("TreeSHAP", shap_imp), ("LIME", li)]:
            top3 = set(np.argsort(-imp)[:3])
            copy_idx = FEATURES.index("tax_revenue_pct_gdp")
            res.append({"variant": variant, "method": name, "rep": rep, "precision_at_3": len(top3 & truth) / 3,
                        "share_on_driver_A": float(imp[A_] / imp.sum()), "share_on_copy_of_A": float(imp[copy_idx] / imp.sum()) if variant == "correlated_copy" else np.nan})
R = pd.DataFrame(res)
agg = R.groupby(["variant", "method"]).agg(precision_at_3=("precision_at_3", "mean"), p3_sd=("precision_at_3", "std"), share_A=("share_on_driver_A", "mean"), share_copy=("share_on_copy_of_A", "mean")).reset_index()
R.to_csv(RES / "17_blend_explanation/sanity.csv", index=False)
print(agg.round(3).to_string())
summary["sanity"] = agg.to_dict("records")
json.dump(summary, open(RES / "17_blend_explanation/summary.json", "w"), indent=1, default=float)
print("done")
