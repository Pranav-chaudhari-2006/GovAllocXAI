"""Experiment D: explainability (SHAP + LIME with the real `lime` package), faithfulness, agreement, stability, and what-if scenarios.
Model explained: XGBoost features-only composition model (one regressor per sector), train <=2019, explain test 2020-2024.
Outputs: results/05_explainability/*.csv|json
"""
import json, sys
import numpy as np, pandas as pd, shap
from scipy.stats import spearmanr
from lime.lime_tabular import LimeTabularExplainer
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from gov_common import *
from xgboost import XGBRegressor

d = load_cofog(); T = TARGETS_A
tr, te = d[d.year <= 2019].reset_index(drop=True), d[d.year >= 2020].reset_index(drop=True)
X = tr[FEATURES]; Xt = te[FEATURES]
models = {}
for c in T:
    m = XGBRegressor(n_estimators=300, learning_rate=0.05, max_depth=3, subsample=0.8, colsample_bytree=0.8, min_child_weight=3,
                     reg_lambda=5.0, random_state=42, n_jobs=-1, verbosity=0)
    models[c] = m.fit(X, tr[c])
focus = ["health", "social_protection", "defence", "education", "transport", "general_public_services"]
fc = {s: f"cofog_{s}_pct_total" for s in focus}
out = {}; glob = {}; shap_vals = {}
for s, c in fc.items():
    sv = shap.TreeExplainer(models[c]).shap_values(Xt)
    shap_vals[s] = sv; glob[s] = np.abs(sv).mean(0)
G = pd.DataFrame(glob, index=FEATURES); G.to_csv(RES / "05_explainability/global_shap.csv")
# all-sector global SHAP (for the heatmap)
allg = {}
for c in T:
    allg[c.replace("cofog_", "").replace("_pct_total", "")] = np.abs(shap.TreeExplainer(models[c]).shap_values(Xt)).mean(0)
pd.DataFrame(allg, index=FEATURES).to_csv(RES / "05_explainability/global_shap_all_sectors.csv")
np.savez(RES / "05_explainability/shap_arrays.npz", **{s: v for s, v in shap_vals.items()}, X=Xt.values)

# ------------- LIME vs SHAP agreement, local fidelity, stability, faithfulness
rng = np.random.default_rng(0)
sample_idx = rng.choice(len(te), size=min(80, len(te)), replace=False)
Xtr_np = X.values; med = np.nanmedian(Xtr_np, 0)
Xtr_f = np.where(np.isnan(Xtr_np), med, Xtr_np)             # lime cannot take NaN: median-fill the (few) NaNs for LIME only
Xt_f = np.where(np.isnan(Xt.values), med, Xt.values)
mu = Xtr_f.mean(0)
agree = []
for s, c in fc.items():
    mdl = models[c]
    pred_fn = lambda a, mdl=mdl: mdl.predict(pd.DataFrame(a, columns=FEATURES))
    expl = LimeTabularExplainer(Xtr_f, feature_names=FEATURES, mode="regression", discretize_continuous=False, random_state=0)
    expl2 = LimeTabularExplainer(Xtr_f, feature_names=FEATURES, mode="regression", discretize_continuous=False, random_state=1)
    rho, jac5, sgn, r2s, stab, delt = [], [], [], [], [], []
    sd = Xtr_f.std(0); sd[sd == 0] = 1
    for i in sample_idx:
        e = expl.explain_instance(Xt_f[i], pred_fn, num_features=len(FEATURES), num_samples=1500)
        w = np.zeros(len(FEATURES))
        for j, v in e.local_exp[1] if 1 in e.local_exp else e.local_exp[list(e.local_exp)[0]]: w[j] = v
        contrib = w * (Xt_f[i] - mu) / sd
        sh = shap_vals[s][i]
        rho.append(spearmanr(np.abs(sh), np.abs(contrib))[0])
        t5s, t5l = set(np.argsort(-np.abs(sh))[:5]), set(np.argsort(-np.abs(contrib))[:5])
        jac5.append(len(t5s & t5l) / len(t5s | t5l))
        top = np.argsort(-np.abs(sh))[:5]; sgn.append(float(np.mean(np.sign(sh[top]) == np.sign(contrib[top]))))
        r2s.append(e.score)
        if len(stab) < 30:
            e2 = expl2.explain_instance(Xt_f[i], pred_fn, num_features=len(FEATURES), num_samples=1500)
            w2 = np.zeros(len(FEATURES))
            for j, v in e2.local_exp[list(e2.local_exp)[0]]: w2[j] = v
            stab.append(spearmanr(np.abs(w), np.abs(w2))[0])
    # faithfulness deletion test (replace top-3 features by train mean): |prediction change|
    base = mdl.predict(Xt.iloc[sample_idx]); res = {}
    for name, rankfn in [("SHAP", lambda i: np.argsort(-np.abs(shap_vals[s][i]))[:3]), ("random", lambda i: rng.choice(len(FEATURES), 3, replace=False))]:
        Z = Xt.iloc[sample_idx].copy().values.astype(float)
        for r_, i in enumerate(sample_idx):
            Z[r_, rankfn(i)] = mu[rankfn(i)] if name == "SHAP" else Z[r_, rankfn(i)]
        # random needs its own indices applied consistently
        if name == "random":
            Z = Xt.iloc[sample_idx].copy().values.astype(float)
            for r_ in range(len(sample_idx)):
                k = rng.choice(len(FEATURES), 3, replace=False); Z[r_, k] = mu[k]
        res[name] = float(np.abs(mdl.predict(pd.DataFrame(Z, columns=FEATURES)) - base).mean())
    agree.append({"sector": s, "spearman_abs_SHAP_vs_LIME": float(np.nanmean(rho)), "top5_jaccard": float(np.mean(jac5)),
                  "top5_sign_agreement": float(np.mean(sgn)), "lime_local_R2": float(np.mean(r2s)), "lime_rerun_spearman": float(np.nanmean(stab)),
                  "deletion_delta_SHAPtop3_pp": res["SHAP"], "deletion_delta_random3_pp": res["random"],
                  "faithfulness_ratio": res["SHAP"] / max(res["random"], 1e-9)})
    print(agree[-1], flush=True)
pd.DataFrame(agree).to_csv(RES / "05_explainability/shap_lime_agreement.csv", index=False)

# ------------- case studies: DEU/ITA/USA 2020 etc (SHAP vs LIME signed contributions)
cases = [("DEU", 2020, "health"), ("USA", 2020, "social_protection"), ("ITA", 2020, "health"), ("JPN", 2022, "defence")]
case_rows = []
for iso, yr, s in cases:
    m_ = te[(te.iso3 == iso) & (te.year == yr)]
    if m_.empty: continue
    i = m_.index[0]; c = fc.get(s) or f"cofog_{s}_pct_total"
    mdl = models[c]; pred_fn = lambda a, mdl=mdl: mdl.predict(pd.DataFrame(a, columns=FEATURES))
    ex = LimeTabularExplainer(Xtr_f, feature_names=FEATURES, mode="regression", discretize_continuous=False, random_state=0)
    e = ex.explain_instance(Xt_f[i], pred_fn, num_features=len(FEATURES), num_samples=3000)
    w = np.zeros(len(FEATURES))
    for j, v in e.local_exp[list(e.local_exp)[0]]: w[j] = v
    sd = Xtr_f.std(0); sd[sd == 0] = 1
    sh = shap.TreeExplainer(mdl).shap_values(Xt.iloc[[i]])[0]
    base = float(shap.TreeExplainer(mdl).expected_value)
    for j, f in enumerate(FEATURES):
        case_rows.append({"case": f"{iso}-{yr}-{s}", "feature": f, "value": float(Xt.iloc[i][f]), "shap": float(sh[j]), "lime_contrib": float(w[j] * (Xt_f[i][j] - mu[j]) / sd[j]),
                          "pred": float(mdl.predict(Xt.iloc[[i]])[0]), "actual": float(te.loc[i, c]), "baseline": base})
pd.DataFrame(case_rows).to_csv(RES / "05_explainability/case_studies.csv", index=False)

# ------------- what-if macro shock (counterfactual sensitivity, NOT causal)
shock = Xt.copy()
shock["log_gdp"] += np.log10(0.85); shock["gdp_per_capita_usd"] *= 0.85; shock["gdp_growth_pct"] -= 15; shock["inflation_pct"] += 12
shock["central_gov_debt_pct_gdp"] += 35
base_p = np.column_stack([models[c].predict(Xt) for c in T]); sh_p = np.column_stack([models[c].predict(shock) for c in T])
base_p, sh_p = simplex_renorm(base_p), simplex_renorm(sh_p)
lo, hi = tr[T].min().values * 0.5, tr[T].max().values * 1.5
sh_al = allocate(sh_p, lo, hi)
W = pd.DataFrame({"sector": [c.replace("cofog_", "").replace("_pct_total", "") for c in T], "baseline_share": base_p.mean(0), "shocked_share": sh_p.mean(0),
                  "shocked_share_after_constraints": sh_al.mean(0), "delta_pp": (sh_p - base_p).mean(0), "delta_sd_over_rows": (sh_p - base_p).std(0)})
W.to_csv(RES / "05_explainability/whatif_shock.csv", index=False); print(W.round(3).to_string())
json.dump({"agreement": agree, "shock_definition": "log10GDP-log10(1/0.85); GDPpc*0.85; growth-15pp; inflation+12pp; debt+35pp"}, open(RES / "05_explainability/summary.json", "w"), indent=1)
print("done")
