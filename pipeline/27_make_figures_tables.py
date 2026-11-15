"""Generate ALL paper figures (PDF+PNG), LaTeX tables and number macros from results/ + data/dataset_new/.
Run after 02-05. Output: papers/figures, papers/tables, papers/results_macros.tex
"""
import json, pathlib, sys
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker
from matplotlib.lines import Line2D
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from gov_common import *

FIG = ROOT / "papers/figures"; TAB = ROOT / "papers/tables"; FIG.mkdir(parents=True, exist_ok=True); TAB.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.spines.top": False, "axes.spines.right": False, "axes.titlesize": 9,
                     "axes.titleweight": "bold", "figure.dpi": 120, "savefig.bbox": "tight"})
PAL = {"base": "#8C8C8C", "persist": "#0072B2", "ml": "#E69F00", "hyb": "#D55E00", "peer": "#009E73", "red": "#CC3311"}
J = lambda p: json.load(open(p))


import matplotlib.text as mtext
FONT_SCALE = 1.45   # figures are drawn ~11 in wide and shown ~6.2 in wide: scale text so it stays >= 7 pt on the page


def save(fig, name):
    for t in fig.findobj(mtext.Text):
        t.set_fontsize(t.get_fontsize() * FONT_SCALE)
    try:
        fig.tight_layout()
    except Exception:  # noqa: BLE001
        pass
    fig.savefig(FIG / f"{name}.pdf"); fig.savefig(FIG / f"{name}.png", dpi=300); plt.close(fig)


def esc(s): return str(s).replace("&", r"\&").replace("_", r"\_").replace("%", r"\%")
NAMES = {"rf": "random forest", "xgb": "XGBoost", "lgbm": "LightGBM", "cat": "CatBoost", "ridge": "ridge regression"}
def pretty(m):
    """Readable method label for tables (no code identifiers)."""
    m = m.replace("Delta-ML Hybrid (50% XGB + 50% CatBoost)", "Delta-learner hybrid (50% XGBoost + 50% CatBoost)").replace("ML Hybrid (50% XGB + 50% CatBoost)", "Hybrid (50% XGBoost + 50% CatBoost)")
    for pre, new in [("Delta-ML (lag + learned change): ", "Delta-learner: "), ("ML features-only: ", "Features-only: "), ("ML: ", "")]:
        if m.startswith(pre):
            k = m[len(pre):]; return new + NAMES.get(k, k)
    return m
CODE = {"peer_mean": "Income-group peer mean", "ridge": "Ridge", "xgb_raw": "XGBoost (raw targets)", "cat_clr": "CatBoost (log-ratio targets)", "xgb_clr": "XGBoost (log-ratio targets)",
        "hybrid_clr": "XGBoost+CatBoost hybrid (log-ratio)", "STACK v2.1 (nested NNLS)": "Stack (nested NNLS)", "persistence": "Persistence (last year)", "country_mean_past": "Country mean of past years",
        "delta_xgb_v2": "Delta-learner: XGBoost", "delta_xgb_hist": "Delta-learner: XGBoost + history features", "delta_cat_hist": "Delta-learner: CatBoost + history features",
        "delta_clr_xgb_hist": "Delta-learner: XGBoost, log-ratio + history", "delta_clr_cat_hist": "Delta-learner: CatBoost, log-ratio + history", "hybrid_clr_hist": "Delta-learner hybrid, log-ratio + history",
        "STACK v2.1 (NNLS on validation)": "Stack (NNLS on validation window)", "knn8": "8-nearest-economies average", "STACK": "Stack (nested NNLS)"}
def code(m): return CODE.get(m, m)
# display labels for legacy sectors (neutral wording)
LEGACY_DISPLAY = {"social welfare freebies": "social welfare schemes", "industry msme": "industry and MSMEs", "digital it": "digital and IT", "housing urban development": "housing and urban development",
                  "water sanitation": "water and sanitation", "environment climate": "environment and climate"}
def f2(x, n=2): return f"{x:.{n}f}"


def booktab(path, header, rows, colfmt, caption, label, star=False, small=True, note=None, size=None, resize=True):
    env = "table*" if star else "table"
    lines = [rf"\begin{{{env}}}", rf"\caption{{{caption}}}\label{{{label}}}", r"\centering" + (("\\" + size) if size else (r"\small" if small else "")) + ("\\setlength{\\tabcolsep}{3pt}" if size else ""), r"\renewcommand{\arraystretch}{1.1}",
             (r"\resizebox{\linewidth}{!}{%" if resize else ""), rf"\begin{{tabular}}{{{colfmt}}}", r"\toprule", " & ".join(header) + r" \\", r"\midrule"]
    for r in rows: lines.append(" & ".join(str(x) for x in r) + r" \\" if r != "MID" else r"\midrule")
    lines += [r"\bottomrule", r"\end{tabular}}" if resize else r"\end{tabular}"]
    if note: lines.append(rf"\par\smallskip{{\footnotesize {note}}}")
    lines.append(rf"\end{{{env}}}")
    pathlib.Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


dq = J(PROC / "govallocxai_new_data_quality.json"); A1 = pd.read_csv(RES / "02_main_experiments/temporal_history.csv"); A2 = pd.read_csv(RES / "02_main_experiments/cold_start.csv")
dyn = pd.read_csv(RES / "02_main_experiments/delta_dynamics.csv"); sumA = J(RES / "02_main_experiments/summary.json"); B = pd.read_csv(RES / "03_wdi_panel/wdi_results.csv"); C = J(RES / "01_legacy_audit/legacy_audit.json")
abl = pd.read_csv(RES / "02_main_experiments/ablation.csv"); bnd = pd.read_csv(RES / "02_main_experiments/bounds_sensitivity.csv"); spec = pd.read_csv(RES / "02_main_experiments/feature_spec_selection.csv")
agree = pd.read_csv(RES / "05_explainability/shap_lime_agreement.csv"); gsh = pd.read_csv(RES / "05_explainability/global_shap_all_sectors.csv", index_col=0)
case = pd.read_csv(RES / "05_explainability/case_studies.csv"); wi = pd.read_csv(RES / "05_explainability/whatif_shock.csv"); sA = J(RES / "02_main_experiments/summary.json")
master = pd.read_csv(PROC / "govallocxai_new_master.csv", usecols=["iso3", "year", "region", "income_group", "cofog_complete_flag", "wdi_target_n", "has_legacy_v1_row", "legacy_only_row", "cofog_source"])
panel = load_cofog()
lab = SECTOR_LABEL

# ======================================================= macros
hyb_name = "Delta-ML Hybrid (50% XGB + 50% CatBoost)"
r_p = A1[A1.method.str.startswith("Persistence")].iloc[0]; r_h = A1[A1.method == hyb_name].iloc[0]
r_cm = A1[A1.method.str.startswith("Country mean")].iloc[0]
a2h = A2[A2.method.str.startswith("ML Hybrid")].iloc[0]; a2p = A2[A2.method.str.startswith("Income-group")].iloc[0]; a2g = A2[A2.method.str.startswith("Global")].iloc[0]
xs = dq["eurostat_vs_oecd_crosscheck"]; nov = int(max(v["n"] for v in xs.values()))
pa = sA["A1_paired"]; pc = sA["A2_paired"]
rep = C["replication"]
ratio = C["ratio_to_gdp"]
M = {
 "NMasterRows": f"{dq['master_rows']:,}".replace(",", "{,}"), "NMasterCols": dq["master_cols"], "NMasterCountries": dq["countries"] - 1,
 "NCofogRows": dq["cofog_panel_rows"], "NCofogCountries": dq["cofog_panel_countries"], "NWdiRows": f"{dq['wdi_panel_rows']:,}".replace(",", "{,}"),
 "NWdiCountries": dq["wdi_panel_countries"], "NLegacyMatched": 750, "NOecdAdded": int(master[master.cofog_source == "OECD NAD Table 11"].iso3.nunique()),
 "NOecdRowsComplete": int(((master.cofog_source == "OECD NAD Table 11")).sum()), "NOverlapRows": nov,
 "NXsrcMedDiff": f2(np.median([v["median_abs_diff_pp"] for v in xs.values()]), 3), "NXsrcMinR": f2(min(v["pearson"] for k, v in xs.items() if k != "communication_digital"), 3),
 "NWdiIndicators": 26, "NFeatNum": 30, "NFeatModel": len(FEATURES), "NSlsqpDiff": f"{sA['engine']['slsqp_vs_exact_max_abs_diff']:.1e}".replace("e-0", r"\times10^{-").replace("e-", r"\times10^{-") + "}" if False else f"{sA['engine']['slsqp_vs_exact_max_abs_diff']:.1e}",
 "ResTVDPersist": f2(r_p.TVD), "ResTVDPersistLo": f2(r_p.TVD_lo), "ResTVDPersistHi": f2(r_p.TVD_hi), "ResTVDHyb": f2(r_h.TVD), "ResTVDHybLo": f2(r_h.TVD_lo), "ResTVDHybHi": f2(r_h.TVD_hi),
 "ResTVDCountryMean": f2(r_cm.TVD), "ResPairedGain": f2(pa["mean_TVD_reduction_vs_persistence"], 3), "ResPairedLo": f2(pa["ci95"][0], 3), "ResPairedHi": f2(pa["ci95"][1], 3),
 "ResRowsImproved": f"{100*pa['share_of_rows_improved']:.0f}", "ResColdHyb": f2(a2h.TVD), "ResColdHybLo": f2(a2h.TVD_lo), "ResColdHybHi": f2(a2h.TVD_hi), "ResColdPeer": f2(a2p.TVD), "ResColdGlobal": f2(a2g.TVD),
 "ResColdGain": f2(pc["hybrid_vs_peer_mean_TVD_reduction"], 2), "ResColdGainLo": f2(pc["ci95"][0], 2), "ResColdGainHi": f2(pc["ci95"][1], 2),
 "ATest": sA["panel"]["A1_test"], "ATrain": sA["panel"]["A1_train"], "AYearLo": sA["panel"]["years"][0], "AYearHi": sA["panel"]["years"][1],
 "LegXGBR": f2(rep["xgb_random_split_R2_usd_mean"], 3), "LegFormulaR": f2(rep["formula_k_x_gdp_R2_usd_mean"], 3), "LegConstRatioR": f2(rep["const_ratio_R2_mean"], 3),
 "LegNConst": C["n_targets_cv_below_0.05"], "LegNIdent": len(C["identical_column_pairs"]), "LegHealthWith": f2(C["healthcare_R2_with_leaky_feature"], 3),
 "LegHealthWithout": f2(C["healthcare_R2_without_leaky_feature"], 3), "LegTempXGB": f2(C["temporal_split_xgb_R2_usd_mean"], 3), "LegTempFormula": f2(C["temporal_split_formula_R2_usd_mean"], 3),
 "EngTVDBefore": f2(sA["engine"]["TVD_before_constraints"], 2),
}
for _, r in agree.iterrows():
    M[f"Agr{r.sector.title().replace('_','')}Rho"] = f2(r.spearman_abs_SHAP_vs_LIME, 2)
M["AgrRhoMean"] = f2(agree.spearman_abs_SHAP_vs_LIME.mean(), 2); M["AgrJacMean"] = f2(agree.top5_jaccard.mean(), 2); M["AgrSignMean"] = f2(agree.top5_sign_agreement.mean(), 2)
M["AgrLimeFit"] = f2(agree.lime_local_R2.mean(), 2); M["AgrStabMean"] = f2(agree.lime_rerun_spearman.mean(), 2); M["AgrFaithMean"] = f2(agree.faithfulness_ratio.mean(), 1)
M["AgrFaithMin"] = f2(agree.faithfulness_ratio.min(), 1); M["AgrFaithMax"] = f2(agree.faithfulness_ratio.max(), 1)
cs_ = [k for k, v in ratio.items() if v["cv"] < 0.05]
M["LegXGBRConst"] = f2(np.mean([rep["xgb_random_split_R2_usd"][k] for k in cs_]), 4); M["LegFormulaRConst"] = f2(np.mean([rep["formula_k_x_gdp_R2_usd"][k] for k in cs_]), 4)
M["LegRealXGB"] = f2(np.mean([v for k, v in rep["xgb_random_split_R2_usd"].items() if k not in cs_]), 3); M["LegRealFormula"] = f2(np.mean([v for k, v in rep["formula_k_x_gdp_R2_usd"].items() if k not in cs_]), 3)
M["LegConstRatioConst"] = f2(np.mean([rep["const_ratio_R2"][k] for k in cs_]), 4); M["LegXGBRatioConst"] = f2(np.mean([rep["xgb_ratio_scale_R2"][k] for k in cs_]), 2)
# NMasterCountries = WB economies in the master table (countries column counts Taiwan, which has only the 25 legacy-only rows, hence -1)
hs = pd.read_csv(RES / "15_robustness_holm/holm.csv"); cm_ = J(RES / "15_robustness_holm/summary.json")["cold_means"]; uu = J(RES / "19_annual_seed_robustness/summary.json")
def hg(pnl, comp): return hs[(hs.panel == pnl) & (hs.comparison == comp)].iloc[0]
def cmean(pnl, meth): return [r for r in cm_ if r["panel"] == pnl and r["method"] == meth][0]["TVD_mean_over_seeds"]
MP = {}
for tag, pnl, comp in [("StackTen", "A10", "STACK vs peer_mean"), ("StackSixteen", "A16", "STACK vs peer_mean"), ("XgbTen", "A10", "xgb_raw vs peer_mean"), ("XgbSixteen", "A16", "xgb_raw vs peer_mean"),
                         ("KnnTen", "A10", "knn8 vs peer_mean"), ("KnnSixteen", "A16", "knn8 vs peer_mean"), ("StackXgbTen", "A10", "STACK vs xgb_raw"), ("StackXgbSixteen", "A16", "STACK vs xgb_raw")]:
    r = hg(pnl, comp)
    MP[f"FS{tag}Gain"] = f2(r.gain_pp_mean_over_seeds, 2); MP[f"FS{tag}Lo"] = f2(r.ci95_lo, 2); MP[f"FS{tag}Hi"] = f2(r.ci95_hi, 2); MP[f"FS{tag}Holm"] = f"{r.p_holm_within_family:.3f}" if r.p_holm_within_family >= 0.01 else f"{r.p_holm_within_family:.4f}"
for tag, pnl, meth in [("PeerTen", "A10", "peer_mean"), ("StackTen", "A10", "STACK"), ("KnnTen", "A10", "knn8"), ("PeerSixteen", "A16", "peer_mean"), ("StackSixteen", "A16", "STACK")]:
    MP[f"FSTVD{tag}"] = f2(cmean(pnl, meth), 2)
MP["ResidualMean"] = f2(panel["cofog_other_residual_pct_total"].mean(), 1); MP["ResidualMedian"] = f2(panel["cofog_other_residual_pct_total"].median(), 1); MP["ResidualMax"] = f2(panel["cofog_other_residual_pct_total"].max(), 1)
MP["AnnSeedMeanGain"] = f2(uu["hybrid"]["mean_gain"], 2); MP["AnnSeedMinGain"] = f2(uu["hybrid"]["min_gain"], 2); MP["AnnSeedMaxGain"] = f2(uu["hybrid"]["max_gain"], 2)
MP["AnnSeedNExcl"] = uu["hybrid"]["n_seeds_ci_excludes_zero"]; MP["AnnSeedN"] = uu["hybrid"]["n_seeds"]
MP["AnnXgbSeedMeanGain"] = f2(uu["xgb"]["mean_gain"], 2)
tx = ["% Macros regenerated by pipeline/27_make_figures_tables.py - do not edit by hand"] + [rf"\newcommand{{\{k}}}{{{v}}}" for k, v in M.items()]
tx += [rf"\newcommand{{\{k}}}{{{v}}}" for k, v in MP.items()]
(ROOT / "papers/results_macros.tex").write_text("\n".join(tx) + "\n", encoding="utf-8")

# ======================================================= Fig 2: data coverage + mean composition
cp = panel.copy(); cp["src"] = cp.cofog_source
ctry = cp.groupby("iso3").year.count().sort_values(ascending=False).index
cov = cp.pivot_table(index="iso3", columns="year", values="cofog_complete_flag", aggfunc="max").reindex(ctry).fillna(0)
fig, ax = plt.subplots(1, 2, figsize=(11, 4.6), gridspec_kw={"width_ratios": [1.1, 1]})
ax[0].imshow(cov.values, aspect="auto", cmap="Blues", vmin=0, vmax=1.3); ax[0].set_yticks(range(len(ctry))); ax[0].set_yticklabels(ctry, fontsize=5.6)
ax[0].set_xticks(range(0, cov.shape[1], 4)); ax[0].set_xticklabels(cov.columns[::4]); ax[0].set_title(f"(a) Complete COFOG country-years (n = {len(cp)})")
Tm = [f"cofog_{s}_pct_total" for s in SECTORS]
qs = cp[Tm].quantile([.1, .5, .9]).T; qs.index = [lab[s] for s in SECTORS]; qs = qs.sort_values(0.5)
ax[1].barh(qs.index, qs[0.5], color=PAL["persist"], alpha=.85); ax[1].errorbar(qs[0.5], range(len(qs)), xerr=[qs[0.5] - qs[0.1], qs[0.9] - qs[0.5]], fmt="none", ecolor="k", lw=.8, capsize=2)
ax[1].set_xlabel("Share of total government expenditure (%)"); ax[1].set_title("(b) Median allocation and 10-90th percentile range"); ax[1].tick_params(axis="y", labelsize=7)
fig.tight_layout(); save(fig, "fig2_data_coverage")

# ======================================================= Fig 3: legacy audit
sec_l = list(ratio.keys()); short = [LEGACY_DISPLAY.get(s.replace("_usd", "").replace("_", " "), s.replace("_usd", "").replace("_", " ")) for s in sec_l]
cvs = [ratio[s]["cv"] * 100 for s in sec_l]; order = np.argsort(cvs)
fig, ax = plt.subplots(1, 3, figsize=(11.5, 3.9))
ax[0].barh(np.array(short)[order], np.array(cvs)[order], color=[PAL["red"] if cvs[i] < 5 else PAL["base"] for i in order]); ax[0].axvline(5, ls="--", c="k", lw=.8)
ax[0].set_xscale("log"); ax[0].set_xlabel("CV of (sector / GDP), %"); ax[0].xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter()); ax[0].set_xticks([2, 5, 10, 50]); ax[0].set_xticklabels(["2", "5", "10", "50"]); ax[0].set_title("(a) 11 of 15 legacy targets are\nfixed multiples of one series"); ax[0].tick_params(axis="y", labelsize=6.5)
x = np.arange(15); w = .38
ax[1].bar(x - w / 2, [rep["xgb_random_split_R2_usd"][s] for s in sec_l], w, color=PAL["ml"], label="XGBoost"); ax[1].bar(x + w / 2, [rep["formula_k_x_gdp_R2_usd"][s] for s in sec_l], w, color=PAL["persist"], label=r"$k\times$GDP (no ML)")
ax[1].set_ylim(0.5, 1.02); ax[1].set_xticks(x[::2]); ax[1].set_xticklabels(list(range(1, 16))[::2], fontsize=6.5); ax[1].set_yticks([.5, .6, .7, .8, .9, 1.0]); ax[1].set_xlabel("legacy sector index"); ax[1].set_ylabel(r"$R^2$ (USD scale)"); ax[1].set_ylim(0.5, 1.22); ax[1].legend(fontsize=6.5, loc="upper center", ncol=2)
ax[1].set_title("(b) USD scale: GDP\nalone explains $R^2$")
ax[2].bar(x - w / 2, [rep["xgb_ratio_scale_R2"][s] for s in sec_l], w, color=PAL["ml"], label="XGBoost"); ax[2].bar(x + w / 2, [rep["const_ratio_R2"][s] for s in sec_l], w, color=PAL["base"], label="constant ratio")
ax[2].axhline(0, c="k", lw=.6); ax[2].set_xticks(x[::2]); ax[2].set_xticklabels(list(range(1, 16))[::2], fontsize=6.5); ax[2].set_yticks([0, .2, .4, .6, .8, 1.0]); ax[2].set_xlabel("legacy sector index"); ax[2].set_ylabel(r"$R^2$ (share-of-GDP scale)"); ax[2].set_ylim(-0.2, 1.3); ax[2].legend(fontsize=6.5, loc="upper center", ncol=2)
ax[2].set_title("(c) Share scale: only\n4 real series learnable")
fig.tight_layout(); save(fig, "fig3_legacy_audit")
pd.DataFrame({"idx": range(1, 16), "sector": short}).to_csv(TAB / "legacy_sector_index.csv", index=False)

# ======================================================= Fig 4: results A1/A2
def bars(ax, df, title, key_persist=None):
    d = df.sort_values("TVD", ascending=False).reset_index(drop=True)
    cols = [PAL["persist"] if m.startswith("Persistence") else PAL["hyb"] if "Hybrid" in m else PAL["peer"] if ("peer" in m or "Country mean" in m or "Global" in m) else PAL["ml"] if "ML" in m else PAL["base"] for m in d.method]
    ax.barh(range(len(d)), d.TVD, color=cols); ax.errorbar(d.TVD, range(len(d)), xerr=[d.TVD - d.TVD_lo, d.TVD_hi - d.TVD], fmt="none", ecolor="k", lw=.8, capsize=2)
    ax.set_yticks(range(len(d))); ax.set_yticklabels([m.replace("Delta-ML (lag + learned change)", "Delta-ML").replace(" (50% XGB + 50% CatBoost)", " (XGB+Cat)").replace("ML features-only", "Features-only") for m in d.method], fontsize=6.8)
    ax.set_xlabel("TVD: % of budget to be moved (lower is better)"); ax.set_title(title)
fig, ax = plt.subplots(1, 2, figsize=(11.5, 4.2)); bars(ax[0], A1, f"(a) Temporal 2020-24 (n = {int(A1.n.iloc[0])})"); bars(ax[1], A2, "(b) Cold start, leave-country-out")
fig.tight_layout(); save(fig, "fig4_main_results")

# ======================================================= Fig 5: per-sector
ms = [c for c in A1.columns if c.startswith("mae_")]; keys = [c.replace("mae_", "") for c in ms]
P_ = A1[A1.method.str.startswith("Persistence")][ms].iloc[0].values; H_ = A1[A1.method == hyb_name][ms].iloc[0].values
fig, ax = plt.subplots(1, 2, figsize=(11.5, 4.1)); y = np.arange(len(keys)); nm = [lab.get(k, "Other / unallocated") for k in keys]
ax[0].barh(y - .2, P_, .4, color=PAL["persist"], label="Persistence"); ax[0].barh(y + .2, H_, .4, color=PAL["hyb"], label="Delta-ML hybrid"); ax[0].set_yticks(y); ax[0].set_yticklabels(nm, fontsize=6.8); ax[0].invert_yaxis()
ax[0].set_xlabel("MAE (pp of total expenditure), 2020-24"); ax[0].legend(fontsize=7, loc="center right"); ax[0].set_title("(a) Per-function error")
dd = dyn.set_index("sector").reindex(keys); ax[1].barh(y, dd.corr_delta.values, color=[PAL["hyb"] if v > .25 else PAL["base"] for v in dd.corr_delta.values]); ax[1].set_yticks(y); ax[1].set_yticklabels(nm, fontsize=6.8); ax[1].invert_yaxis()
ax[1].set_xlabel("Correlation: predicted vs actual year-on-year change"); ax[1].axvline(0, c="k", lw=.6); ax[1].set_title("(b) Does the model anticipate shifts?")
fig.tight_layout(); save(fig, "fig5_per_function")

# ======================================================= Fig 6: WDI panel
tg = ["wdi_health_pct_gdp", "wdi_rnd_pct_gdp", "wdi_education_pct_gdp", "wdi_defence_pct_gdp"]; tl = ["Health\n%GDP", "R&D\n%GDP", "Education\n%GDP", "Defence\n%GDP"]
fig, ax = plt.subplots(1, 3, figsize=(11.5, 3.6), sharey=False)
for a, (proto, meths, ttl) in zip(ax, [("B2 leave-country-out", ["Income-group peer mean", "ML: ridge", "Hybrid (XGB+Cat)"], "(a) Leave-country-out"), ("B3 leave-region-out", ["Income-group peer mean", "ML: ridge", "Hybrid (XGB+Cat)"], "(b) Leave-region-out"),
                                       ("B1 temporal+history", ["Persistence", "Country mean", "Delta-ML Hybrid (XGB+Cat)"], "(c) Temporal 2019-24, with history")]):
    sub = B[(B.protocol == proto) & B.method.isin(meths)]
    for i, m in enumerate(meths):
        v = [sub[(sub.method == m) & (sub.target == t)].R2.values[0] for t in tg]
        a.bar(np.arange(4) + (i - 1) * .27, v, .27, label=m.replace("Delta-ML Hybrid (XGB+Cat)", "Delta-ML hybrid"), color=[PAL["peer"], PAL["base"], PAL["hyb"]][i] if proto != "B1 temporal+history" else [PAL["persist"], PAL["base"], PAL["hyb"]][i])
    a.set_xticks(range(4)); a.set_xticklabels(tl, fontsize=7); a.axhline(0, c="k", lw=.6); a.set_title(ttl); lo, hi = a.get_ylim(); a.set_ylim(lo, hi + (hi - lo) * 0.55); a.legend(fontsize=6.3, loc="upper right"); a.set_ylabel(r"$R^2$"); a.set_yticks([t for t in a.get_yticks() if t <= 1.0001])
fig.tight_layout(); save(fig, "fig6_wdi_panel")

# ======================================================= Fig 7: SHAP global heatmap
g = gsh.copy(); g.columns = [lab.get(c, "Other") for c in g.columns]; top = g.mean(1).sort_values(ascending=False).index[:14]
gn = g.loc[top] / g.max(0)
fig, ax = plt.subplots(figsize=(9.8, 4.6)); im = ax.imshow(gn.values, aspect="auto", cmap="YlOrRd", vmin=0, vmax=1)
ax.set_yticks(range(len(top))); ax.set_yticklabels([FEATURE_LABEL[t] for t in top], fontsize=7); ax.set_xticks(range(g.shape[1])); ax.set_xticklabels(g.columns, rotation=60, ha="right", fontsize=7)
cb = fig.colorbar(im, fraction=.025, pad=.01); cb.set_label("mean |SHAP| / sector maximum", fontsize=7); ax.set_title("Global SHAP importance of the 14 strongest features, per budget function (test years 2020-24)")
fig.tight_layout(); save(fig, "fig7_global_shap")

# ======================================================= Fig 8: SHAP vs LIME (case studies + agreement)
cs = case.case.unique()[:2]
fig, ax = plt.subplots(1, 3, figsize=(12.2, 4.0), gridspec_kw={"width_ratios": [1, 1, .9]})
for a, c in zip(ax[:2], cs):
    q = case[case.case == c].copy(); q = q.reindex(q.shap.abs().sort_values(ascending=False).index).head(8).iloc[::-1]
    yy = np.arange(len(q)); a.barh(yy - .19, q.shap, .38, color=PAL["hyb"], label="TreeSHAP"); a.barh(yy + .19, q.lime_contrib, .38, color=PAL["persist"], label="LIME")
    a.set_yticks(yy); a.set_yticklabels([FEATURE_LABEL[f] for f in q.feature], fontsize=6.8); a.axvline(0, c="k", lw=.6)
    r = q.iloc[0]; a.set_title(f"{c.replace('-', ' ')}" + chr(10) + f"pred {r.pred:.1f}% vs actual {r.actual:.1f}%", fontsize=8); a.set_xlabel("contribution to predicted share (pp)")
ax[0].legend(fontsize=7, loc="center right")
ag = agree.set_index("sector"); xs_ = np.arange(len(ag))
ax[2].bar(xs_ - .27, ag.spearman_abs_SHAP_vs_LIME, .27, color=PAL["persist"], label=r"Spearman $\rho$"); ax[2].bar(xs_, ag.top5_jaccard, .27, color=PAL["ml"], label="top-5 Jaccard"); ax[2].bar(xs_ + .27, ag.top5_sign_agreement, .27, color=PAL["peer"], label="top-5 sign agr.")
ax[2].set_xticks(xs_); ax[2].set_xticklabels([{"Social Protection": "Social prot.", "General Public Services": "Gen. public"}.get(lab.get(s, s), lab.get(s, s)) for s in ag.index], fontsize=6, rotation=40, ha="right"); ax[2].set_ylim(0, 1.45); ax[2].legend(fontsize=6.3, ncol=1, loc="upper right"); ax[2].set_title("SHAP-LIME agreement" + chr(10) + "(80 test rows per function)", fontsize=8)
fig.tight_layout(); save(fig, "fig8_shap_vs_lime")

# ======================================================= Fig 9: what-if + bounds
w2 = wi.copy(); w2["name"] = [lab.get(s, "Other / unallocated") for s in w2.sector]; w2 = w2.sort_values("delta_pp")
fig, ax = plt.subplots(1, 2, figsize=(11.2, 4.0), gridspec_kw={"width_ratios": [1.3, 1]})
ax[0].barh(w2.name, w2.delta_pp, xerr=w2.delta_sd_over_rows, color=[PAL["hyb"] if v > 0 else PAL["persist"] for v in w2.delta_pp], error_kw={"lw": .7, "ecolor": "k"}); ax[0].axvline(0, c="k", lw=.6)
ax[0].set_xlabel("Mean change in recommended share (pp) [bar = sd across rows]"); ax[0].set_title("(a) What-if: severe macro shock\n(GDP -15%, inflation +12 pp, debt +35 pp)"); ax[0].tick_params(axis="y", labelsize=7)
ax[1].bar(range(len(bnd)), bnd.TVD, color=[PAL["base"], PAL["ml"], PAL["hyb"], PAL["persist"]]); ax[1].set_xticks(range(len(bnd))); ax[1].set_xticklabels([b.replace(" - ", "-\n").replace(" (", "\n(") for b in bnd.bounds], fontsize=6.6)
ax[1].set_ylim(0, max(bnd.TVD) * 1.15); ax[1].set_ylabel("TVD vs actual (pp)"); ax[1].set_title("(b) Allocation-engine bound width\n(temporal test, Delta-hybrid)")
for i, (v, o) in enumerate(zip(bnd.TVD, bnd.rows_pred_outside_bounds)): ax[1].text(i, v + .05, f"{o*100:.0f}% rows\nclipped", ha="center", fontsize=6)
fig.tight_layout(); save(fig, "fig9_whatif_engine")

# ======================================================= Fig 10: COVID delta scatter
pb = pd.read_csv(RES / "02_main_experiments/best_predictions.csv"); lagp = panel[["iso3", "year"] + [f"lag_{t}" for t in TARGETS_A]]
mm = pb.merge(lagp, on=["iso3", "year"]); mm = mm[mm.year.isin([2020, 2021])]
fig, ax = plt.subplots(1, 3, figsize=(11.4, 3.6)); COV = {}
for a, s in zip(ax, ["health", "social_protection", "education"]):
    t = f"cofog_{s}_pct_total"; da = mm[f"act_{t}"] - mm[f"lag_{t}"]; dp_ = mm[f"pred_{t}"] - mm[f"lag_{t}"]
    a.scatter(da, dp_, s=14, c=np.where(mm.year == 2020, PAL["hyb"], PAL["persist"]), alpha=.8); lim = max(abs(da).max(), abs(dp_).max()) * 1.1; a.plot([-lim, lim], [-lim, lim], "k--", lw=.7); a.axhline(0, c="gray", lw=.5); a.axvline(0, c="gray", lw=.5)
    a.set_xlabel("actual change vs previous year (pp)"); a.set_ylabel("predicted change (pp)"); a.set_title(f"{lab[s]}" + chr(10) + f"(pooled 2020-21, r = {np.corrcoef(da, dp_)[0,1]:.2f})")
    COV[s] = float(np.corrcoef(da, dp_)[0, 1])
ax[0].legend(handles=[Line2D([], [], marker="o", ls="", c=PAL["hyb"], label="2020"), Line2D([], [], marker="o", ls="", c=PAL["persist"], label="2021")], fontsize=7)
fig.tight_layout(); save(fig, "fig10_covid_shift")
with open(ROOT / "papers/results_macros.tex", "a", encoding="utf-8") as fh:
    fh.write("\n".join([rf"\newcommand{{\CovPooledHealth}}{{{COV['health']:.2f}}}", rf"\newcommand{{\CovPooledSocial}}{{{COV['social_protection']:.2f}}}", rf"\newcommand{{\CovPooledEducation}}{{{COV['education']:.2f}}}",
                         rf"\newcommand{{\CovTwentyHealth}}{{{sA['covid']['health']['corr_2020']:.2f}}}", rf"\newcommand{{\CovTwentySocial}}{{{sA['covid']['social_protection']['corr_2020']:.2f}}}"]) + "\n")

# ======================================================= Tables
FG = {"log_gdp": "Macro", "log_pop": "Demography", "gdp_per_capita_usd": "Macro", "gdp_growth_pct": "Macro", "inflation_pct": "Macro", "urban_pop_pct": "Demography", "pop_65plus_pct": "Demography",
      "pop_0_14_pct": "Demography", "tax_revenue_pct_gdp": "Fiscal", "central_gov_debt_pct_gdp": "Fiscal", "total_expense_pct_gdp": "Fiscal", "unemployment_pct": "Macro", "life_expectancy": "Health",
      "under5_mortality": "Health", "internet_users_pct": "Development", "electricity_access_pct": "Development", "basic_water_access_pct": "Development", "co2_per_capita_t": "Environment",
      "agri_value_added_pct_gdp": "Structure", "industry_value_added_pct_gdp": "Structure", "trade_pct_gdp": "Structure", "gov_effectiveness_wgi": "Governance", "control_corruption_wgi": "Governance",
      "rule_of_law_wgi": "Governance", "regulatory_quality_wgi": "Governance"}
booktab(TAB / "tab_features.tex", ["Feature", "Group", "Source", "Imputed cells (\\%)"],
        [[esc(FEATURE_LABEL[f]), FG[f], "WGI" if "wgi" in f else "WDI", f"{dq['feature_imputed_cells_pct'].get({'log_gdp':'gdp_usd','log_pop':'population'}.get(f,f),0):.1f}"] for f in FEATURES],
        "lll r".replace(" ", ""), "The 25 model features (all from WDI/WGI; derived log transforms of GDP and population). Imputed-cell share is over the full master table.", "tab:features", small=True)
booktab(TAB / "tab_sdg.tex", ["COFOG function", "Primary SDG(s)"], [[esc(lab[s]), ", ".join(f"SDG~{g}" for g in SDG_MAP[s])] for s in SECTORS],
        "ll", "Reporting cross-walk from COFOG functions to SDGs. It is a reporting layer chosen by the authors, \\emph{not} a model input and not an official UN mapping.", "tab:sdg")
booktab(TAB / "tab_hyper.tex", ["Model", "Hyper-parameters"],
        [["XGBoost", "300 trees, lr 0.05, depth 3, subsample 0.8, colsample 0.8, min child weight 3, $L_2$ = 5"], ["LightGBM", "300 trees, lr 0.05, 8 leaves, min child 10, subsample 0.8, colsample 0.8, $L_2$ = 5"],
         ["CatBoost", "300 iterations, lr 0.07, depth 4, $L_2$ = 5"], ["Random Forest", "300 trees, min leaf 3, max features 0.5"], ["Ridge", r"$\alpha=10$, standardised inputs, median imputation"],
         ["Hybrid", "$0.5\\,\\hat{y}_{\\text{XGB}}+0.5\\,\\hat{y}_{\\text{Cat}}$"], ["All", "targets standardised; seed 42; no tuning on test data (Section~\\ref{sec:selection})"]],
        "lp{9.5cm}", "Fixed hyper-parameters (no test-set tuning).", "tab:hyper")
rowsA = []
for _, r in A1.iterrows(): rowsA.append([esc(pretty(r.method)), f"{r.TVD:.2f}", f"[{r.TVD_lo:.2f}, {r.TVD_hi:.2f}]", f"{r.RMSE_pp:.3f}"])
booktab(TAB / "tab_A1.tex", ["Method", "TVD (pp)", "95\\% CI", "RMSE (pp)"], rowsA, "lccc",
        f"Temporal evaluation: train 2000--2019, test 2020--2024 ($n={int(A1.n.iloc[0])}$ country-years, {sA['panel']['A1_test_countries']} economies); one-step-ahead with last year's allocation available. CIs: cluster bootstrap over economies. (MAE is omitted: with 17 components it equals TVD/8.5 exactly.)", "tab:A1", star=False)
rowsB = [[esc(pretty(r.method)), f"{r.TVD:.2f}", f"[{r.TVD_lo:.2f}, {r.TVD_hi:.2f}]", f"{r.TVD_sd_over_foldseeds:.2f}"] for _, r in A2.iterrows()]
booktab(TAB / "tab_A2.tex", ["Method", "TVD (pp)", "95\\% CI", "SD over fold seeds"], rowsB, "lccc",
        f"Cold-start evaluation: leave-country-out (6 folds, 2 fold seeds; TVD is the mean over both seeds), all {sA['panel']['rows']} country-years, no history available.", "tab:A2")
# WDI table
def wdi_cell(proto, meth, t, col="R2"): return B[(B.protocol == proto) & (B.method == meth) & (B.target == t)][col].values[0]
tnames = {"wdi_health_pct_gdp": "Health (%GDP)", "wdi_rnd_pct_gdp": "R&D (%GDP)", "wdi_education_pct_gdp": "Education (%GDP)", "wdi_defence_pct_gdp": "Defence (%GDP)", "wdi_health_pct_govexp": "Health (%gov. exp.)",
          "wdi_education_pct_govexp": "Education (%gov. exp.)", "wdi_defence_pct_govexp": "Defence (%gov. exp.)"}
rowsW = []
for t, n in tnames.items():
    rowsW.append([esc(n), int(B[(B.protocol == "B2 leave-country-out") & (B.target == t)].n.iloc[0]), f"{wdi_cell('B2 leave-country-out','Income-group peer mean',t):.2f}", f"{wdi_cell('B2 leave-country-out','Hybrid (XGB+Cat)',t):.2f}",
                  f"{wdi_cell('B3 leave-region-out','Income-group peer mean',t):.2f}", f"{wdi_cell('B3 leave-region-out','Hybrid (XGB+Cat)',t):.2f}",
                  f"{wdi_cell('B1 temporal+history','Persistence',t):.2f}", f"{wdi_cell('B1 temporal+history','Delta-ML Hybrid (XGB+Cat)',t):.2f}"])
booktab(TAB / "tab_B.tex", ["Official series", "$n$", "LCO peer", "LCO hybrid", "LRO peer", "LRO hybrid", "Persist.", "$\\Delta$-hybrid"], rowsW, "lrcccccc",
        r"WDI global panel, $R^2$. LCO = leave-country-out, LRO = leave-region-out: income-group peer mean vs.\ XGBoost+CatBoost hybrid. \emph{Temporal}: train $\le$2018, test 2019--2024, persistence vs.\ $\Delta$-hybrid with last-year value.", "tab:B", star=True)
rowsX = [[esc(lab.get(r.sector, r.sector)), f"{r.spearman_abs_SHAP_vs_LIME:.2f}", f"{r.top5_jaccard:.2f}", f"{r.top5_sign_agreement:.2f}", f"{r.lime_local_R2:.2f}", f"{r.lime_rerun_spearman:.2f}", f"{r.faithfulness_ratio:.1f}"] for _, r in agree.iterrows()]
rowsX.append("MID"); rowsX.append(["Mean", f"{agree.spearman_abs_SHAP_vs_LIME.mean():.2f}", f"{agree.top5_jaccard.mean():.2f}", f"{agree.top5_sign_agreement.mean():.2f}", f"{agree.lime_local_R2.mean():.2f}", f"{agree.lime_rerun_spearman.mean():.2f}", f"{agree.faithfulness_ratio.mean():.1f}"])
booktab(TAB / "tab_xai.tex", ["Function", "Spearman $\\rho$", "Top-5 Jaccard", "Top-5 sign agr.", "LIME local $R^2$", "LIME re-run $\\rho$", "Faithfulness ratio"], rowsX, "lcccccc",
        "Quantitative evaluation of SHAP and LIME (80 random test rows per function). Faithfulness ratio = mean |prediction change| when the three most important SHAP features are reset to the training mean, divided by the same for three random features.", "tab:xai", star=True)
booktab(TAB / "tab_ablation.tex", ["Feature set", "\\#features", "TVD (pp)", "SD over seeds"], [[esc(r.variant), r.n_features, f"{r.TVD:.2f}", f"{r.sd:.2f}"] for _, r in abl.iterrows()], "lccc",
        "Cold-start feature-group ablation (XGBoost, leave-country-out). Each row removes one group. SD is the population SD over the two fold seeds (ddof = 0), so it is not comparable with the sample SD in Table~\\ref{tab:A2}.", "tab:ablation")
booktab(TAB / "tab_bounds.tex", ["Bounds", "TVD (pp)", "Predicted rows clipped (\\%)", "Actual rows outside (\\%)"], [[esc(r.bounds.replace("0.5x", "0.5$\\times$").replace("1.5x", "1.5$\\times$")), f"{r.TVD:.3f}", f"{100*r.rows_pred_outside_bounds:.1f}", f"{100*r.actual_rows_outside_bounds:.1f}"] for _, r in bnd.iterrows()], "lccc",
        "Allocation-engine sensitivity to the width of the policy bounds (temporal test, $\\Delta$-hybrid).", "tab:bounds")
booktab(TAB / "tab_selection.tex", ["Regime", "Feature spec", "\\#features", "Validation TVD (pp)"], [[esc(r.regime), esc(r.spec), r.n_features, f"{r.TVD_val:.3f}"] for _, r in spec.iterrows()], "llcc",
        "Feature-spec selection on a validation window (train $\\le$2016, validate 2017--2019; test years never used). In the cold-start regime richer specifications did not improve validation error. In the history regime the ``changes'' specification improved on the base specification (2.27 vs.\\ 2.33\\,pp) but remained worse than persistence (2.26\\,pp); the base 25 features were kept.", "tab:selection")
rowsL = []
for i, s in enumerate(sec_l):
    rowsL.append([i + 1, esc(short[i]), f"{ratio[s]['mean_pct']:.2f}", f"{ratio[s]['cv']*100:.1f}", f"{rep['xgb_random_split_R2_usd'][s]:.3f}", f"{rep['formula_k_x_gdp_R2_usd'][s]:.3f}", f"{rep['xgb_ratio_scale_R2'][s]:.2f}", f"{rep['const_ratio_R2'][s]:.2f}"])
booktab(TAB / "tab_audit.tex", ["\\#", "Legacy sector", "Mean \\%GDP", "CV (\\%)", "$R^2$ XGB (USD)", "$R^2$ $k\\!\\times$GDP (USD)", "$R^2$ XGB (share)", "$R^2$ const. (share)"], rowsL, "rlcccccc",
        r"Forensic re-analysis of the legacy v1 benchmark (random 80/20 split as in the original notebooks). CV = coefficient of variation of sector/GDP across all 775 rows.", "tab:audit", star=True)
# ---- v2.1: wider panel (A10, IMF) + architecture Stack + income-group analysis
import os
if os.path.exists(RES / "04_stack_architecture/summary.json") and os.path.exists(RES / "06_cold_start_by_income/cold_by_income.csv"):
    E = J(RES / "04_stack_architecture/summary.json"); F = pd.read_csv(RES / "06_cold_start_by_income/cold_by_income.csv"); Fa = J(RES / "06_cold_start_by_income/applicability.json")
    def crow(kind, name): return pd.read_csv(RES / f"04_stack_architecture/{kind}_cold.csv").query("method == @name").iloc[0]
    def hrow(kind, name): return pd.read_csv(RES / f"04_stack_architecture/{kind}_history.csv").query("method == @name").iloc[0]
    st16, pe16 = crow("A16", "STACK v2.1 (nested NNLS)"), crow("A16", "peer_mean")
    st10, pe10 = crow("A10", "STACK v2.1 (nested NNLS)"), crow("A10", "peer_mean")
    single10 = pd.read_csv(RES / "04_stack_architecture/A10_cold.csv"); best10 = single10[~single10.method.isin(["peer_mean", "STACK v2.1 (nested NNLS)"])].sort_values("TVD").iloc[0]
    hp10, hs10 = hrow("A10", "persistence"), hrow("A10", "STACK v2.1 (NNLS on validation)")
    hb10 = pd.read_csv(RES / "04_stack_architecture/A10_history.csv").query("method not in ['persistence', 'country_mean_past', 'STACK v2.1 (NNLS on validation)']").sort_values("TVD_test").iloc[0]
    M2 = {"NTenRows": dq["cofog10_panel_rows"], "NTenEcon": dq["cofog10_panel_countries"], "NTenImf": dq["cofog10_by_source"].get("IMF GFS_COFOG", 0),
          "ColdStackSixteen": f2(st16.TVD), "ColdPeerSixteen": f2(pe16.TVD), "ColdStackTen": f2(st10.TVD), "ColdStackTenLo": f2(st10.TVD_lo), "ColdStackTenHi": f2(st10.TVD_hi),
          "ColdPeerTen": f2(pe10.TVD), "ColdBestTen": f2(best10.TVD), "HistPersistTen": f2(hp10.TVD_test), "HistStackTen": f2(hs10.TVD_test), "HistBestTen": f2(hb10.TVD_test),
          "NovRho": f2(Fa["spearman_novelty_vs_TVD_xgb"], 2), "ErrHigh": f2(F[F.income_group == "High income"].TVD_xgb.iloc[0], 1), "ErrLow": f2(F[F.income_group == "Low income"].TVD_xgb.iloc[0], 1),
          "ErrLowerMid": f2(F[F.income_group == "Lower middle income"].TVD_xgb.iloc[0], 1)}
    with open(ROOT / "papers/results_macros.tex", "a", encoding="utf-8") as fh:
        fh.write("\n".join(rf"\newcommand{{\{k}}}{{{v}}}" for k, v in M2.items()) + "\n")
    rowsE = []
    for kind, lab_ in [("A16", "A16 (36 economies)"), ("A10", "A10 (85 economies)")]:
        cdf = pd.read_csv(RES / f"04_stack_architecture/{kind}_cold.csv").sort_values("TVD")
        for _, r in cdf.iterrows():
            rowsE.append([lab_, esc(code(r.method)), f"{r.TVD:.2f}", f"[{r.TVD_lo:.2f}, {r.TVD_hi:.2f}]"])
        rowsE.append("MID")
    rowsE = rowsE[:-1]
    booktab(TAB / "tab_E_cold.tex", ["Panel", "Method", "TVD (pp)", "95\\% CI"], rowsE, "llcc",
            "Architecture v2.1, cold start (leave-country-out, 6 folds; TVD and CI are means over 2 fold seeds): peer mean, single learners (raw or log-ratio targets) and the nested-NNLS stack. Paired gains over the peer mean in the text are five-seed values (Table~\\ref{tab:holm}), so they differ slightly from differences of the two-seed means shown here.", "tab:Ecold")
    rowsH = []
    for kind in ["A16", "A10"]:
        hdf = pd.read_csv(RES / f"04_stack_architecture/{kind}_history.csv")
        for _, r in hdf.iterrows():
            rowsH.append([kind, esc(code(r.method)), f"{r.TVD_val:.2f}", f"{r.TVD_test:.2f}", f"[{r.TVD_test_lo:.2f}, {r.TVD_test_hi:.2f}]"])
        rowsH.append("MID")
    rowsH = rowsH[:-1]
    booktab(TAB / "tab_E_hist.tex", ["Panel", "Method", "Val. TVD", "Test TVD", "Test 95\\% CI"], rowsH, "llccc",
            "Architecture v2.1, annual update (one-step-ahead). Stack weights are fitted on the validation window; the test window 2020--24 is used once.", "tab:Ehist", star=False)
    booktab(TAB / "tab_income.tex", ["Income group", "Economies", "Country-years", "Novelty", "Peer mean", "Ridge", "XGBoost"],
            [[esc(r.income_group), int(r.economies), int(r.country_years), f"{r.mean_novelty:.2f}", f"{r.TVD_peer_mean:.1f}", f"{r.TVD_ridge:.1f}", f"{r.TVD_xgb:.1f}"] for _, r in F.iterrows()], "lcccccc",
            "Cold-start error (TVD, pp) by World Bank income group on the wide panel A10, with the mean applicability (novelty) score.", "tab:income")
    booktab(TAB / "tab_income_conf.tex", ["Income group", "Econ.", "Novelty", "Peer mean", "XGBoost"],
            [[esc(r.income_group.replace(" income", "")), int(r.economies), f"{r.mean_novelty:.2f}", f"{r.TVD_peer_mean:.1f}", f"{r.TVD_xgb:.1f}"] for _, r in F.iterrows()], "lcccc",
            "Cold-start TVD (pp) by income group on the wide panel A10 (50/23/9/3 economies) with the mean applicability (novelty) score. The low-income group has only three economies.", "tab:income", size="footnotesize", resize=False)
    hist16 = hrow("A16", "STACK v2.1 (NNLS on validation)")
    with open(ROOT / "papers/results_macros.tex", "a", encoding="utf-8") as fh:
        fh.write(rf"\newcommand{{\HistStackSixteen}}{{{f2(hist16.TVD_test)}}}" + "\n")
if os.path.exists(RES / "07_total_budget/total_budget.csv"):
    G = pd.read_csv(RES / "07_total_budget/total_budget.csv")
    def g_(proto, m): return G[(G.protocol == proto) & (G.method == m)].iloc[0]
    M3 = {"TotPersist": f2(g_("temporal 2020-24", "persistence").MAE_pp_gdp), "TotDeltaRidge": f2(g_("temporal 2020-24", "delta ridge").MAE_pp_gdp),
          "TotColdMean": f2(g_("cold start leave-country-out", "income-group mean").MAE_pp_gdp), "TotColdRidge": f2(g_("cold start leave-country-out", "ridge").MAE_pp_gdp)}
    with open(ROOT / "papers/results_macros.tex", "a", encoding="utf-8") as fh:
        fh.write("\n".join(rf"\newcommand{{\{k}}}{{{v}}}" for k, v in M3.items()) + "\n")
    booktab(TAB / "tab_G_total.tex", ["Protocol", "Method", "$n$", "MAE (pp of GDP)", "95\\% CI"],
            [[esc(r.protocol), esc(r.method), int(r.n), f"{r.MAE_pp_gdp:.2f}", f"[{r.lo:.2f}, {r.hi:.2f}]"] for _, r in G.iterrows()], "llccc",
            "Total-budget module: general-government total expenditure as percent of GDP (30 OECD/EU economies, 716 country-years, Eurostat COFOG panel). MAE in percentage points of GDP. The income-group mean equals the global mean because all but one economy is high income.", "tab:total")
# ---- five-seed Holm table
hl = {"STACK vs peer_mean": "Stack vs peer mean", "xgb_raw vs peer_mean": "XGBoost vs peer mean", "knn8 vs peer_mean": "8-nearest-economies vs peer mean", "STACK vs xgb_raw": "Stack vs XGBoost"}
rowsHm = []
for pnl in ["A16", "A10"]:
    for comp, nm_ in hl.items():
        r = hg(pnl, comp)
        rowsHm.append([pnl, nm_, f"{r.gain_pp_mean_over_seeds:.2f}", f"[{r.ci95_lo:.2f}, {r.ci95_hi:.2f}]", (f"{r.p_holm_within_family:.3f}" if r.p_holm_within_family >= 0.01 else f"{r.p_holm_within_family:.4f}"), "yes" if r["survives_holm_0.05_family"] else "no"])
booktab(TAB / "tab_holm.tex", ["Panel", "Comparison (cold start)", "Gain (pp)", "95\\% CI", "Holm $p$", "Survives?"], rowsHm, "llcccc",
        "Cold-start paired TVD gains averaged over five fold seeds, cluster bootstrap over economies (10\\,000 draws), Holm correction over the family of eight comparisons. Positive = first method better.", "tab:holm")
# ---- compact conference versions
keepA1 = ["Persistence (last year)", "Country mean (train)", "ML features-only: xgb", "Delta-ML (lag + learned change): xgb", "Delta-ML (lag + learned change): cat", hyb_name]
nm = lambda m: pretty(m).replace("Delta-learner hybrid (50% XGBoost + 50% CatBoost)", "Delta-learner hybrid").replace(" (last year)", "").replace(" (train)", "")
booktab(TAB / "tab_A1_conf.tex", ["Method", "TVD (pp)", "95\\% CI"], [[esc(nm(r.method)), f"{r.TVD:.2f}", f"[{r.TVD_lo:.2f}, {r.TVD_hi:.2f}]"] for _, r in A1[A1.method.isin(keepA1)].iterrows()], "lcc",
        f"Temporal test 2020--24 ($n={int(A1.n.iloc[0])}$), one-step-ahead, TVD in percentage points.", "tab:A1", size="footnotesize", resize=False)
keepA2 = ["Global mean", "Income-group peer mean", "ML: ridge", "ML: xgb", "ML Hybrid (50% XGB + 50% CatBoost)"]
booktab(TAB / "tab_A2_conf.tex", ["Method", "TVD (pp)", "95\\% CI"], [[esc(nm(r.method).replace("Hybrid (50% XGBoost + 50% CatBoost)", "Hybrid (XGBoost+CatBoost)")), f"{r.TVD:.2f}", f"[{r.TVD_lo:.2f}, {r.TVD_hi:.2f}]"] for _, r in A2[A2.method.isin(keepA2)].iterrows()], "lcc",
        r"Cold start: leave-country-out (6 folds $\times$ 2 seeds, mean over seeds), TVD in percentage points.", "tab:A2", size="footnotesize", resize=False)
import re as _re
for _f in ["tab_B.tex", "tab_audit.tex", "tab_A1.tex"]:   # typographic minus signs in numeric cells
    _p = TAB / _f
    _lines = _p.read_text(encoding="utf-8").split("\n")
    _lines = [_re.sub(r"(?<![\w\-])-(\d)", r"$-$\1", l) if "&" in l else l for l in _lines]
    _p.write_text("\n".join(_lines), encoding="utf-8")
print("figures:", sorted(p.name for p in FIG.glob("*.pdf")))
print("tables:", sorted(p.name for p in TAB.glob("*.tex")))
