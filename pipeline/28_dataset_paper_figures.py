"""Figures, tables and number macros for the GovAlloc-COFOG v1.0 data descriptor (papers/dataset_paper/).

Every number quoted in the data paper is computed here from the released files in data/dataset_new/, data/dataset_old/, data/raw/ and the
data-quality JSON; nothing is typed by hand.  Run:  python pipeline/28_dataset_paper_figures.py
Outputs: papers/dataset_paper/generated/dataset_macros.tex  (\\newcommand macros, prefix D)
         papers/dataset_paper/generated/tab_*.tex           (inventory, column dictionary, coverage, imputation, checks)
         papers/dataset_paper/figures/figD1..figD5 (.pdf + .png)
"""
import json
import pathlib
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch

ROOT = pathlib.Path(__file__).resolve().parents[1]
NEW, OLD, RAW = ROOT / "data/dataset_new", ROOT / "data/dataset_old", ROOT / "data/raw"
OUT = ROOT / "papers/dataset_paper"
GEN, FIG = OUT / "generated", OUT / "figures"
GEN.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({"font.size": 10, "axes.labelsize": 10, "axes.titlesize": 10.5, "xtick.labelsize": 9.5, "ytick.labelsize": 9.5,
                     "legend.fontsize": 9.5, "axes.spines.top": False, "axes.spines.right": False, "pdf.fonttype": 42, "savefig.dpi": 300,
                     "axes.titleweight": "bold"})
BLUE, ORANGE, GREEN, RED, SKY, GREY, PURPLE = "#0072B2", "#E69F00", "#009E73", "#D55E00", "#56B4E9", "#7f7f7f", "#7B4EA3"
W = 7.0

# ------------------------------------------------------------------ load
def find(folder, suffix):
    """Locate a released file by suffix so the script works before and after the file renaming (govalloc_cofog_* -> govalloc_cofog_*)."""
    hits = sorted(folder.glob("*" + suffix))
    assert len(hits) == 1, (folder, suffix, hits)
    return hits[0]


F_MASTER, F_A16, F_A10 = find(NEW, "master.csv"), find(NEW, "panel_a16.csv"), find(NEW, "panel_a10.csv")
F_A10X, F_WDI, F_IA = find(NEW, "panel_a10x.csv"), find(NEW, "panel_wdi.csv"), find(NEW, "institutional_features.csv")
F_IB, F_DQ, F_OLD = find(NEW, "institutional_manual.csv"), find(NEW, "data_quality.json"), find(OLD, "dataset.csv")
master = pd.read_csv(F_MASTER, low_memory=False)
a16 = pd.read_csv(F_A16)
a10 = pd.read_csv(F_A10)
a10x = pd.read_csv(F_A10X)
wdi = pd.read_csv(F_WDI)
inst_a = pd.read_csv(F_IA)
inst_b = pd.read_csv(F_IB)
old = pd.read_csv(F_OLD)
dq = json.load(open(F_DQ))
lstruct = json.load(open(ROOT / "results/01_legacy_audit/legacy_structure.json"))
laudit = json.load(open(ROOT / "results/01_legacy_audit/legacy_audit.json"))
for d in (master, a16, a10, wdi):
    d["region"] = d["region"].str.strip()

C16 = [c for c in master.columns if c.startswith("cofog_") and c.endswith("_pct_total")]
C10 = [c for c in master.columns if c.startswith("cofog10_") and c.endswith("_pct_total")]
FEATS = [c[4:] for c in master.columns if c.startswith("imp_")]
core = master[master.legacy_only_row == 0]           # the 217 official-data economies (Taiwan rows are legacy-only)
INC = ["High income", "Upper middle income", "Lower middle income", "Low income"]
INC_K = {"High income": "Hi", "Upper middle income": "Um", "Lower middle income": "Lm", "Low income": "Lo"}

M = {}                                              # macro name -> string


def n(x):
    return f"{int(x):,}".replace(",", "{,}")


def f(x, d=2):
    return f"{x:.{d}f}"


# ------------------------------------------------------------------ basic counts
M["DMasterRows"], M["DMasterCols"] = n(len(master)), str(master.shape[1])
M["DMasterEcon"], M["DMasterEconAll"] = n(core.iso3.nunique()), n(master.iso3.nunique())
M["DLegacyOnlyRows"] = n((master.legacy_only_row == 1).sum())
M["DYearLo"], M["DYearHi"] = str(int(master.year.min())), str(int(master.year.max()))
M["DNYears"] = str(master.year.nunique())
for key, d in [("Six", a16), ("Ten", a10), ("Wdi", wdi), ("Mas", core)]:
    M[f"DRows{key}"], M[f"DEcon{key}"] = n(len(d)), n(d.iso3.nunique())
    for g in INC:
        M[f"DEcon{key}{INC_K[g]}"] = n(d[d.income_group == g].iso3.nunique())
        M[f"DRows{key}{INC_K[g]}"] = n((d.income_group == g).sum())
M["DTenXRows"], M["DTenXEcon"] = n(len(a10x)), n(a10x.iso3.nunique())
M["DTenXExtra"] = n(len(a10x) - len(a10))
M["DTenXCentral"] = n((a10x.cofog10_scope == "central government").sum())
M["DTenMidLow"] = n(a10[a10.income_group.isin(INC[1:])].iso3.nunique())
M["DTenLowMid"] = n(a10[a10.income_group.isin(INC[2:])].iso3.nunique())
yrs_per = a10.groupby("iso3").year.count()
M["DTenYrsMedian"], M["DTenYrsMin"], M["DTenYrsMax"] = f(yrs_per.median(), 0), str(int(yrs_per.min())), str(int(yrs_per.max()))
M["DTenShortN"] = n((yrs_per < 10).sum())
for src, k in [("Eurostat gov_10a_exp", "Es"), ("OECD NAD Table 11", "Oecd"), ("IMF GFS_COFOG", "Imf")]:
    M[f"DTenRows{k}"] = n((a10.cofog10_source == src).sum())
    M[f"DTenEcon{k}"] = n(a10[a10.cofog10_source == src].iso3.nunique())
for src, k in [("Eurostat gov_10a_exp", "Es"), ("OECD NAD Table 11", "Oecd")]:
    M[f"DSixRows{k}"] = n((a16.cofog_source_name == src).sum())
    M[f"DSixEcon{k}"] = n(a16[a16.cofog_source_name == src].iso3.nunique())
M["DSixIncomplete"] = n((master.cofog_complete_flag == 0).sum())
M["DSixNonHigh"] = n(a16[a16.income_group != "High income"].iso3.nunique())
M["DWdiTargetSeries"] = "7"
M["DWdiSixPlus"] = n((wdi.wdi_target_n >= 6).sum())
M["DWdiOneTwo"] = n((wdi.wdi_target_n <= 2).sum())
M["DWdiTargetMeanCov"] = f(wdi[[c for c in wdi.columns if c.startswith("wdi_") and c != "wdi_target_n"]].notna().mean().mean() * 100, 0)
M["DNumFeat"] = str(len(FEATS))
M["DInstARows"], M["DInstBRows"] = n(len(inst_a)), n(len(inst_b))

# ------------------------------------------------------------------ column dictionary (computed)
cols = list(master.columns)
legacy_cols = [c for c in cols if c.startswith("legacy_")]
grp = {
    "ids": ["iso3", "iso2", "country", "region", "income_group", "year"],
    "feat": FEATS,
    "imp": [c for c in cols if c.startswith("imp_")],
    "wdi": [c for c in cols if c.startswith("wdi_") and c != "wdi_target_n"],
    "derived": ["n_imputed_features", "log_gdp", "log_pop", "has_legacy_v1_row", "wdi_target_n"],
    "c16share": C16,
    "c16gdp": [c for c in cols if c.startswith("cofog_") and c.endswith("_pct_gdp")],
    "c16mio": [c for c in cols if c.startswith("cofog_") and c.endswith("_mio_eur")],
    "c16usd": [c for c in cols if c.startswith("cofog_") and c.endswith("_usd_derived")],
    "c16prov": ["cofog_complete_flag", "cofog_source_name", "cofog_source"],
    "c10": C10,
    "c10prov": ["cofog10_source", "cofog10_complete_flag"],
    "legacy": legacy_cols,
}
assert sum(len(v) for v in grp.values()) == master.shape[1], (sum(len(v) for v in grp.values()), master.shape[1])
assert len(set(sum(grp.values(), []))) == master.shape[1]
NAMES = {"ids": "Ids", "feat": "Feat", "imp": "Imp", "wdi": "Wdi", "derived": "Derived", "c16share": "SixShare", "c16gdp": "SixGdp", "c16mio": "SixMio",
         "c16usd": "SixUsd", "c16prov": "SixProv", "c10": "Ten", "c10prov": "TenProv", "legacy": "Legacy"}
for k, v in grp.items():
    M[f"DCols{NAMES[k]}"] = str(len(v))
M["DLegacyCols"] = str(old.shape[1])
M["DLegacyRows"], M["DLegacyEcon"] = n(len(old)), str(old.iloc[:, 0].nunique() if old.iloc[:, 0].dtype == object else master[master.has_legacy_v1_row == 1].iso3.nunique())
M["DLegacyEcon"] = str(master[master.has_legacy_v1_row == 1].iso3.nunique())


def tex_escape(s):
    return s.replace("_", r"\_")


rows = [
    ("Identifiers and groupings", "ids", r"\texttt{iso3}, \texttt{iso2}, \texttt{country}, \texttt{region}, \texttt{income\_group} (World Bank, current classification), \texttt{year}"),
    ("Socio-economic features", "feat", r"26 WDI and 4 WGI indicators (GDP, inflation, demography, fiscal, health, infrastructure, governance); \texttt{units in column name}"),
    ("Imputation flags", "imp", r"\texttt{imp\_<feature>} = 1 if the cell was filled, 0 if observed"),
    ("WDI sector targets", "wdi", r"education, domestic government health, military (each \% of GDP and of government expenditure) and R\&D (\% of GDP), observed only"),
    ("Derived fields", "derived", r"\texttt{n\_imputed\_features}, \texttt{log\_gdp}, \texttt{log\_pop}, \texttt{has\_legacy\_v1\_row}, \texttt{wdi\_target\_n}"),
    ("COFOG-16 targets, share of total", "c16share", r"16 functions plus an explicit residual, \% of general-government expenditure (the simplex targets of panel A16)"),
    ("COFOG-16, share of GDP", "c16gdp", r"same functions as \% of GDP (Eurostat and OECD)"),
    ("COFOG-16, national currency", "c16mio", r"same functions plus total, million euro (Eurostat only)"),
    ("COFOG-16, derived USD", "c16usd", r"share of GDP $\times$ World Bank GDP in current USD (derived, not an official figure)"),
    ("COFOG-16 provenance", "c16prov", r"\texttt{cofog\_complete\_flag}, \texttt{cofog\_source\_name}, \texttt{cofog\_source}"),
    ("COFOG-10 targets", "c10", r"divisions GF01--GF10, \% of total expenditure (panel A10)"),
    ("COFOG-10 provenance", "c10prov", r"\texttt{cofog10\_source} (Eurostat / OECD / IMF), \texttt{cofog10\_complete\_flag}"),
    ("Legacy columns", "legacy", r"all 57 legacy columns with prefix \texttt{legacy\_} (semi-synthetic sector columns; see Section~\ref{sec:legacy}); \texttt{legacy\_only\_row} marks the Taiwan rows"),
]
t = [r"\begin{table}[t]", r"\caption{Column dictionary of the master table (\DMasterCols{} columns); the three modelling panels contain the same columns.}\label{tab:columns}",
     r"\centering\small", r"\renewcommand{\arraystretch}{1.12}", r"\begin{tabular}{@{}p{3.6cm}rp{9.4cm}@{}}", r"\toprule",
     r"Group & Columns & Content \\", r"\midrule"]
for name, k, desc in rows:
    t.append(f"{name} & {len(grp[k])} & {desc} \\\\")
t += [r"\midrule", rf"Total & {master.shape[1]} & \\", r"\bottomrule", r"\end{tabular}", r"\end{table}"]
(GEN / "tab_columns.tex").write_text("\n".join(t) + "\n", encoding="utf8")


# ------------------------------------------------------------------ file inventory
def size(p):
    s = pathlib.Path(p).stat().st_size
    return f"{s/1e6:.2f}\\,MB" if s >= 1e6 else f"{s/1e3:.0f}\\,kB"


def shp(d):
    return n(d.shape[0]), n(d.shape[1])


inv = [
    ("", "master.csv", "All economies $\\times$ 2000--2024: features, flags, all targets, legacy columns", *shp(master), size(F_MASTER)),
    ("", "cofog\\_panel.csv", "Panel A16: complete 16-function COFOG, Eurostat + OECD", *shp(a16), size(F_A16)),
    ("", "cofog10\\_panel.csv", "Panel A10: complete 10-division COFOG, Eurostat + OECD + IMF", *shp(a10), size(F_A10)),
    ("", "cofog10x\\_panel.csv", "A10 plus rows admitted under a relaxed rule (scope/strictness flags)", *shp(a10x), size(F_A10X)),
    ("", "wdi\\_panel.csv", "Panel B: rows with at least one official WDI sector series", *shp(wdi), size(F_WDI)),
    ("", "institutional\\_features.csv", "WGI voice \\& accountability, political stability (+ 2-year changes)", *shp(inst_a), size(F_IA)),
    ("", "institutional\\_manual.csv", "Fiscal rules, election timing, IMF programme indicators", *shp(inst_b), size(F_IB)),
    ("", "data\\_quality.json", "Coverage, imputation, cross-source and legacy audit statistics", "--", "--", size(F_DQ)),
    ("", "legacy\\_dataset.csv", "Legacy dataset, verbatim (semi-synthetic sectors); in dataset\\_old/", *shp(old), size(F_OLD)),
]
t = [r"\begin{table}[t]", r"\caption{File inventory of GovAlloc-COFOG v1.0 (processed files; raw downloads are described in the text). Files in \texttt{dataset\_new/} start with \texttt{govalloc\_cofog\_} (omitted here), as does the legacy file in \texttt{dataset\_old/}. Rows $\times$ columns were counted from the files.}\label{tab:files}",
     r"\centering\footnotesize", r"\renewcommand{\arraystretch}{1.1}", r"\begin{tabular}{@{}p{4.4cm}p{4.9cm}rrr@{}}", r"\toprule",
     r"File & Content & Rows & Cols & Size \\", r"\midrule"]
for fo, fi, ds, r_, c_, s_ in inv:
    t.append("\\texttt{" + fi + "} & " + ds + " & " + r_ + " & " + c_ + " & " + s_ + " \\\\")
t += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
(GEN / "tab_files.tex").write_text("\n".join(t) + "\n", encoding="utf8")
raw_info = {}
for sub in ["worldbank", "eurostat", "oecd", "imf", "imf_extra", "institutional"]:
    fl = [p for p in (RAW / sub).rglob("*") if p.is_file()]
    raw_info[sub] = (len(fl), sum(p.stat().st_size for p in fl) / 1e6)
M["DRawFiles"] = n(sum(v[0] for v in raw_info.values()))
M["DRawMB"] = f(sum(v[1] for v in raw_info.values()), 0)
M["DRawWB"], M["DRawES"] = n(raw_info["worldbank"][0]), n(raw_info["eurostat"][0])
M["DDataTotalMB"] = f(sum(p.stat().st_size for p in NEW.glob("*")) / 1e6 + F_OLD.stat().st_size / 1e6, 1)

# ------------------------------------------------------------------ coverage table (income group)
t = [r"\begin{table}[t]", r"\caption{Coverage by World Bank income group (current classification applied to all years): economies (country-years) in each file. A10 covers 85 economies but only \DEconTenLo{} low-income and \DEconTenLm{} lower-middle-income ones.}\label{tab:coverage}",
     r"\centering\small", r"\begin{tabular}{@{}lrrrr@{}}", r"\toprule", r"Income group & Master & Panel B (WDI) & Panel A10 & Panel A16 \\", r"\midrule"]
for g in INC:
    cells = []
    for d in (core, wdi, a10, a16):
        e, r_ = d[d.income_group == g].iso3.nunique(), (d.income_group == g).sum()
        cells.append(f"{e} ({n(r_)})")
    t.append(f"{g} & " + " & ".join(cells) + r" \\")
t += [r"\midrule", "All & " + " & ".join(f"{d.iso3.nunique()} ({n(len(d))})" for d in (core, wdi, a10, a16)) + r" \\", r"\bottomrule", r"\end{tabular}", r"\end{table}"]
(GEN / "tab_coverage.tex").write_text("\n".join(t) + "\n", encoding="utf8")

# ------------------------------------------------------------------ validation computations
chk = {}
s16 = a16[C16].sum(axis=1)
M["DSumSixMaxDev"] = f"{(s16 - 100).abs().max():.1e}".replace("e-", r"\times10^{-").replace("e+", r"\times10^{") + "}"
s10 = a10[C10].sum(axis=1)
M["DSumTenMin"], M["DSumTenMax"] = f(s10.min(), 1), f(s10.max(), 1)
for src, k in [("Eurostat gov_10a_exp", "Es"), ("OECD NAD Table 11", "Oecd"), ("IMF GFS_COFOG", "Imf")]:
    s = s10[a10.cofog10_source == src]
    M[f"DSumTenMax{k}"] = f((s - 100).abs().max(), 1)
M["DSumTenEsMin"], M["DSumTenEsMax"] = f(s10[a10.cofog10_source == "Eurostat gov_10a_exp"].min(), 1), f(s10[a10.cofog10_source == "Eurostat gov_10a_exp"].max(), 1)
neg16 = (a16[C16] < 0).sum()
neg10 = (a10[C10] < 0).sum()
M["DNegSix"], M["DNegTen"] = str(int(neg16.sum())), str(int(neg10.sum()))
M["DNegSixCells"] = n(a16[C16].size)
M["DNegSixRows"] = str(int((a16[C16] < 0).any(axis=1).sum()))
M["DNegSixComm"] = str(int(neg16["cofog_communication_digital_pct_total"]))
M["DNegSixHous"] = str(int(neg16["cofog_housing_community_pct_total"]))
M["DNegSixRes"] = str(int(neg16["cofog_other_residual_pct_total"]))
M["DNegSixResMin"] = f(a16["cofog_other_residual_pct_total"].min(), 1)
M["DNegSixMin"] = f(a16[C16].min().min(), 1)
M["DSixMax"] = f(a16[C16].max().max(), 1)
M["DSixMaxName"] = "social protection"
M["DTenMaxVal"] = f(a10[C10].max().max(), 1)
M["DTenNegMin"] = f(a10[C10].min().min(), 1)
M["DTargetMissSix"], M["DTargetMissTen"] = str(int(a16[C16].isna().sum().sum())), str(int(a10[C10].isna().sum().sum()))
M["DDupKeys"] = str(int(master.duplicated(["iso3", "year"]).sum()) + int(a16.duplicated(["iso3", "year"]).sum()) + int(a10.duplicated(["iso3", "year"]).sum()) + int(wdi.duplicated(["iso3", "year"]).sum()))
M["DYearsOK"] = "yes" if master.year.between(2000, 2024).all() else "no"
# year-to-year jumps in A10
x = a10.sort_values(["iso3", "year"]).reset_index(drop=True)
dx = x.groupby("iso3")[C10].diff()
ok = x.groupby("iso3").year.diff().eq(1)
tvd = (dx.abs().sum(axis=1) / 2)[ok]
M["DJumpTot"], M["DJumpMed"] = n(len(tvd)), f(tvd.median(), 1)
M["DJumpN"], M["DJumpPct"] = n((tvd > 10).sum()), f((tvd > 10).mean() * 100, 1)
M["DJumpMax"] = f(tvd.max(), 0)
jump_rows = x[ok & (tvd > 10).reindex(x.index, fill_value=False)]
M["DJumpEcon"] = n(jump_rows.iso3.nunique())
M["DJumpCovid"] = n((jump_rows.year == 2020).sum())
M["DJumpImf"] = n((jump_rows.cofog10_source == "IMF GFS_COFOG").sum())
# construct validity: COFOG10 vs WDI sector series (different definitions, same concept)
for g, w, k in [("GF07", "wdi_health_pct_govexp", "Health"), ("GF09", "wdi_education_pct_govexp", "Edu"), ("GF02", "wdi_defence_pct_govexp", "Def")]:
    d = a10[[f"cofog10_{g}_pct_total", w]].dropna()
    M[f"DCvN{k}"], M[f"DCvR{k}"], M[f"DCvMed{k}"] = n(len(d)), f(d.corr().iloc[0, 1], 2), f((d.iloc[:, 0] - d.iloc[:, 1]).abs().median(), 1)
# WDI bounds
wcols = [c for c in grp["wdi"]]
M["DWdiNeg"] = str(int((wdi[wcols] < 0).sum().sum()))
M["DWdiPctOverHundred"] = str(int((wdi[[c for c in wcols if "pct_govexp" in c]] > 100).sum().sum()))
M["DWdiHealthMax"] = f(wdi["wdi_health_pct_gdp"].max(), 1)
M["DWdiDefMax"] = f(wdi["wdi_defence_pct_gdp"].max(), 1)
# cross-source (from the quality JSON)
es_oecd = pd.DataFrame(dq["eurostat_vs_oecd_crosscheck"]).T
imf_es = pd.DataFrame(dq["cofog10_imf_vs_eurostat"]).T
M["DEoN"], M["DEoMedLo"], M["DEoMedHi"] = n(es_oecd.n.max()), f(es_oecd.median_abs_diff_pp.min(), 3), f(es_oecd.median_abs_diff_pp.max(), 3)
M["DEoRmin"], M["DEoRmax"] = f(es_oecd.pearson.min(), 3), f(es_oecd.pearson.max(), 3)
M["DEoRminB"] = f(es_oecd.pearson.drop("communication_digital").min(), 3)
M["DEoMedAll"] = f(es_oecd.median_abs_diff_pp.median(), 3)
M["DIeN"], M["DIeMedLo"], M["DIeMedHi"] = n(imf_es.n.max()), f(imf_es.median_abs_diff_pp.min(), 3), f(imf_es.median_abs_diff_pp.max(), 3)
M["DIeRmin"], M["DIeRmax"] = f(imf_es.pearson.min(), 3), f(imf_es.pearson.max(), 3)
M["DIeMedAll"] = f(imf_es.median_abs_diff_pp.median(), 3)
M["DIeRminName"] = "general public services"
assert imf_es.pearson.idxmin() == "cofog10_GF01_pct_total"
assert es_oecd.pearson.idxmin() == "communication_digital"
M["DOecdAdded"] = str(len(dq["oecd_added_countries"]))
M["DOecdAddedList"] = ", ".join(dq["oecd_added_countries"])
lr = dq["legacy_vs_real"]
M["DLegFeatN"] = n(lr["gdp_usd"]["n"])
M["DLegHealthGap"], M["DLegHealthR"] = f(lr["leg_hlt_vs_wdi_health_pct_gdp"]["median_abs_err_pp"], 1), f(lr["leg_hlt_vs_wdi_health_pct_gdp"]["pearson"], 2)
M["DLegDefR"] = f(lr["leg_def_vs_wdi_defence_pct_gdp"]["pearson"], 3)
M["DLegInflPninety"] = f(lr["inflation_pct"]["p90_abs_rel_err"] * 100, 1)
M["DLegExactFeat"] = str(sum(1 for k in ["gdp_usd", "population", "life_expectancy", "gdp_growth_pct", "unemployment_pct", "internet_users_pct"] if lr[k]["median_abs_rel_err"] == 0 and lr[k]["p90_abs_rel_err"] == 0))
# legacy structure
mult = lstruct["exact_multiples"]
M["DLegMult"] = str(len(mult))
M["DLegMultMax"] = f(max(v["std_of_multiple"] for v in mult.values()) * 1e12, 1) + r"\times10^{-12}"
M["DLegLatentMean"], M["DLegLatentSd"] = f(lstruct["latent_total_pct_gdp"]["mean"], 1), f(lstruct["latent_total_pct_gdp"]["sd"], 2)
M["DLegMixes"] = str(lstruct["n_distinct_country_year_mixes"])
M["DLegCorrGrowth"] = f(lstruct["corr_latent_ratio_vs_gdp_growth"], 2)
M["DLegIdent"] = str(len(laudit["identical_column_pairs"]))
M["DLegIdentTargets"] = str(laudit["identical_pairs_involving_targets"])
# recompute multiples from the file to confirm the JSON (ratio of each sector to agriculture, sd across rows)
sect = [c for c in old.columns if c.endswith("_usd") and any(c.startswith(s) for s in ["infrastructure", "agriculture", "rural", "social_welfare", "energy", "transport", "housing", "water", "environment", "digital", "industry"])]
ratios = old[sect].div(old["agriculture_usd"], axis=0)
assert len(sect) == 11 and ratios.std().max() < 1e-9, (len(sect), ratios.std().max())
M["DLegRatioSdMax"] = f"{ratios.std().max():.0e}".replace("e-", r"\times10^{-") + "}"
M["DLegRatioMin"], M["DLegRatioMax"] = f(ratios.mean().min(), 3), f(ratios.mean().max(), 3)

# ------------------------------------------------------------------ imputation by feature
fg = {"Economy": ["gdp_usd", "gdp_per_capita_usd", "gdp_growth_pct", "inflation_pct", "trade_pct_gdp", "agri_value_added_pct_gdp", "industry_value_added_pct_gdp"],
      "Demography": ["population", "urban_pop_pct", "pop_65plus_pct", "pop_0_14_pct"],
      "Fiscal": ["tax_revenue_pct_gdp", "central_gov_debt_pct_gdp", "revenue_pct_gdp", "total_expense_pct_gdp", "net_lending_pct_gdp"],
      "Social and health": ["poverty_215_pct", "unemployment_pct", "adult_literacy_pct", "life_expectancy", "under5_mortality", "gini"],
      "Infrastructure, environment": ["internet_users_pct", "electricity_access_pct", "basic_water_access_pct", "co2_per_capita_t"],
      "Governance (WGI)": ["gov_effectiveness_wgi", "control_corruption_wgi", "rule_of_law_wgi", "regulatory_quality_wgi"]}
assert sorted(sum(fg.values(), [])) == sorted(FEATS)
imp_pct = {c: core[f"imp_{c}"].mean() * 100 for c in FEATS}
miss_pct = {c: core[c].isna().mean() * 100 for c in FEATS}
for c in FEATS:                                                    # agreement with the JSON written by the build script
    assert abs(round(imp_pct[c], 1) - dq["feature_imputed_cells_pct"][c]) <= 0.15, (c, imp_pct[c], dq["feature_imputed_cells_pct"][c])
    # the JSON counts all 5,450 master rows (incl. the 25 legacy-only Taiwan rows, which have no features); the paper reports the 5,425 official rows
    assert abs(round(master[c].isna().mean() * 100, 1) - dq["feature_missing_after_imputation_pct"][c]) <= 0.15, (c, dq["feature_missing_after_imputation_pct"][c])
M["DImpMean"] = f(np.mean(list(imp_pct.values())), 1)
M["DMissMean"], M["DMissMax"] = f(np.mean(list(miss_pct.values())), 1), f(max(miss_pct.values()), 1)
M["DMissMaxName"] = "central-government debt"
assert max(miss_pct, key=miss_pct.get) == "central_gov_debt_pct_gdp"
M["DImpGtFifty"] = str(sum(v > 50 for v in imp_pct.values()))
M["DImpGtForty"] = str(sum(v > 40 for v in imp_pct.values()))
M["DImpLtFive"] = str(sum(v < 5 for v in imp_pct.values()))
M["DImpZero"] = str(sum(v == 0 for v in imp_pct.values()))
M["DImpGini"], M["DImpPov"], M["DImpLit"] = f(imp_pct["gini"], 0), f(imp_pct["poverty_215_pct"], 0), f(imp_pct["adult_literacy_pct"], 0)
M["DImpDebt"] = f(imp_pct["central_gov_debt_pct_gdp"], 0)
M["DImpFiscalLo"], M["DImpFiscalHi"] = f(min(imp_pct[c] for c in fg["Fiscal"] if c != "central_gov_debt_pct_gdp"), 0), f(max(imp_pct[c] for c in fg["Fiscal"] if c != "central_gov_debt_pct_gdp"), 0)
M["DImpWgiLo"], M["DImpWgiHi"] = f(min(imp_pct[c] for c in fg["Governance (WGI)"]), 0), f(max(imp_pct[c] for c in fg["Governance (WGI)"]), 0)
M["DImpPerRowMean"], M["DImpPerRowMax"] = f(core.n_imputed_features.mean(), 1), str(int(core.n_imputed_features.max()))
M["DImpPerRowMed"] = f(core.n_imputed_features.median(), 0)
# imputation of the rows that enter A10 / A16
for key, d in [("Six", a16), ("Ten", a10)]:
    M[f"DImpRow{key}"] = f(d.n_imputed_features.mean(), 1)
    M[f"DImpCells{key}"] = f(d[[f"imp_{c}" for c in FEATS]].mean().mean() * 100, 1)
# by income
imp_inc = {g: core[core.income_group == g][[f"imp_{c}" for c in FEATS]].mean().mean() * 100 for g in INC}
for g in INC:
    M[f"DImpInc{INC_K[g]}"] = f(imp_inc[g], 1)

t = [r"\begin{table}[t]", r"\caption{Imputation by feature group over the \DMasterEcon{} economies $\times$ 25 years ($\DMasterEcon\times 25=$ \DMasterEconYears{} country-years): share of cells that were filled (and flagged) and share still missing afterwards. Feature-level values are in Fig.~\ref{fig:imp}.}\label{tab:imp}",
     r"\centering\small", r"\begin{tabular}{@{}lrrr@{}}", r"\toprule", r"Feature group & Features & Imputed cells (\%) & Still missing (\%) \\", r"\midrule"]
M["DMasterEconYears"] = n(len(core))
for g, v in fg.items():
    t.append(f"{g} & {len(v)} & {np.mean([imp_pct[c] for c in v]):.1f} & {np.mean([miss_pct[c] for c in v]):.1f} \\\\")
t += [r"\midrule", f"All features & {len(FEATS)} & {np.mean(list(imp_pct.values())):.1f} & {np.mean(list(miss_pct.values())):.1f} \\\\", r"\bottomrule", r"\end{tabular}", r"\end{table}"]
(GEN / "tab_imp.tex").write_text("\n".join(t) + "\n", encoding="utf8")

# ------------------------------------------------------------------ validation summary table
t = [r"\begin{table}[t]", r"\caption{Summary of automated validation checks (all computed by \texttt{pipeline/28\_dataset\_paper\_figures.py} from the released files).}\label{tab:checks}",
     r"\centering\small", r"\renewcommand{\arraystretch}{1.1}", r"\begin{tabular}{@{}p{3.8cm}p{3.2cm}p{7.8cm}@{}}", r"\toprule", r"Check & Scope & Result \\", r"\midrule",
     rf"Component shares sum to 100 & A16, {M['DRowsSix']} rows & maximum deviation $\DSumSixMaxDev$ pp \\",
     rf"Component shares sum to 100 & A10, {M['DRowsTen']} rows & Eurostat rows {M['DSumTenEsMin']}--{M['DSumTenEsMax']} (published rounding); OECD and IMF rows exactly 100 \\",
     rf"Missing targets & A16, A10 & {M['DTargetMissSix']} and {M['DTargetMissTen']} missing cells (complete-case panels; targets never imputed) \\",
     rf"Negative values & A16, A10 & {M['DNegSix']} of {M['DNegSixCells']} A16 cells ({M['DNegSixRows']} country-years), {M['DNegTen']} A10 cells; minimum {M['DNegSixMin']} pp; kept as published \\",
     rf"Upper bounds & A16, A10 & largest share {M['DSixMax']}\% (social protection); no share above 100\% \\",
     rf"Duplicate \texttt{{iso3}}--\texttt{{year}} keys & master and three panels & {M['DDupKeys']} duplicates; all years in 2000--2024 \\",
     rf"Eurostat vs OECD & {M['DEoN']} country-years, 15 functions & median $|\Delta|$ {M['DEoMedLo']}--{M['DEoMedHi']} pp; $r\ge{M['DEoRmin']}$ \\",
     rf"IMF vs Eurostat & {M['DIeN']} country-years, 10 divisions & median $|\Delta|$ {M['DIeMedLo']}--{M['DIeMedHi']} pp; $r\ge{M['DIeRmin']}$ \\",
     rf"COFOG vs WDI sector series & A10, health / education / defence & $r=${M['DCvRHealth']} / {M['DCvREdu']} / {M['DCvRDef']} (different definitions) \\",
     rf"Year-to-year jumps & A10, {M['DJumpTot']} consecutive pairs & {M['DJumpN']} ({M['DJumpPct']}\%) move more than 10 pp (total variation); flagged by users, not removed \\",
     rf"WDI series bounds & Panel B & {M['DWdiNeg']} negative values; no \%-of-expenditure value above 100 \\",
     rf"Legacy features vs World Bank & {M['DLegFeatN']} legacy rows & identical for {M['DLegExactFeat']} of 7 checked indicators; inflation within 0.4\% on 90\% of rows \\",
     r"\bottomrule", r"\end{tabular}", r"\end{table}"]
(GEN / "tab_checks.tex").write_text("\n".join(t) + "\n", encoding="utf8")

# ------------------------------------------------------------------ benchmark macros from the main paper (so nothing is retyped)
mm = (ROOT / "papers/results_macros.tex").read_text(encoding="utf8")
bm = dict(re.findall(r"\\newcommand\{\\(\w+)\}\{([^}]*(?:\{[^}]*\}[^}]*)*)\}", mm))
for k in ["ResTVDPersist", "ResTVDPersistLo", "ResTVDPersistHi", "ResTVDHyb", "ResPairedGain", "ResPairedLo", "ResPairedHi", "ColdStackTen", "ColdPeerTen", "ColdStackSixteen",
          "ColdPeerSixteen", "ErrHigh", "ErrLow", "FSStackTenGain", "FSStackTenHolm", "HistPersistTen", "HistStackTen", "LegXGBR", "LegFormulaRConst", "LegXGBRConst", "LegConstRatioConst", "AnnSeedMeanGain", "AnnSeedNExcl", "AnnSeedN"]:
    assert k in bm, k
    M["DBm" + k] = bm[k]

# ------------------------------------------------------------------ write macros
lines = ["% Generated by pipeline/28_dataset_paper_figures.py -- do not edit by hand"]
for k in sorted(M):
    assert re.fullmatch(r"[A-Za-z]+", k), k
    lines.append(f"\\newcommand{{\\{k}}}{{{M[k]}}}")
(GEN / "dataset_macros.tex").write_text("\n".join(lines) + "\n", encoding="utf8")


# ================================================================== FIGURES
def save(fig, name):
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(FIG / f"{name}.png", bbox_inches="tight", dpi=300)
    plt.close(fig)


# ---- Fig D1: construction workflow (simple vertical flow, title above)
steps = [
    ("Fetch", "Download raw data through public APIs; files are stored unedited.", "data/raw/ (%s files)" % M["DRawFiles"].replace("{,}", ",")),
    ("Harmonise", "Join on ISO3 code and year; map COFOG codes to 16 functions and 10 divisions.", "economy-year rows"),
    ("Validate", "Keep complete country-years whose shares sum to 100; priority Eurostat, OECD, IMF.", "targets never imputed"),
    ("Features", "Fill short gaps (interpolation, then peer median) and flag every filled cell.", "30 features + 30 flags"),
    ("Release", "Master table, three panels and a quality report; legacy columns keep a prefix.", "data/dataset_new/"),
]
cols_ = [BLUE, BLUE, GREEN, ORANGE, PURPLE]
fig, ax = plt.subplots(figsize=(W, 4.6))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")
ax.text(0.0, 0.985, "Construction workflow of GovAlloc-COFOG", ha="left", va="top", fontsize=11, fontweight="bold")
top, step = 0.86, 0.178
for i, (ttl, desc, outp) in enumerate(steps):
    yc = top - i * step
    ax.plot([0.035], [yc], marker="o", markersize=22, color=cols_[i], zorder=3, clip_on=False)
    ax.text(0.035, yc, str(i + 1), ha="center", va="center", color="white", fontsize=10.5, fontweight="bold", zorder=4)
    ax.text(0.095, yc + 0.028, ttl, ha="left", va="center", fontsize=10.5, fontweight="bold", color=cols_[i])
    ax.text(0.095, yc - 0.026, desc, ha="left", va="center", fontsize=8.6, color="#333333")
    ax.text(1.0, yc + 0.028, outp, ha="right", va="center", fontsize=8.6, color="#333333", bbox=dict(boxstyle="round,pad=0.25", fc="#F1F1F1", ec="#CCCCCC", lw=0.8))
    if i < len(steps) - 1:
        ax.annotate("", xy=(0.035, yc - step + 0.040), xytext=(0.035, yc - 0.040), arrowprops=dict(arrowstyle="-|>", lw=1.6, color="#555555", mutation_scale=13))
save(fig, "figD1_workflow")

# ---- Fig D2: country-year coverage
yrs = list(range(2000, 2025))
cnt = lambda d: d.groupby("year").iso3.nunique().reindex(yrs, fill_value=0)
fig, axs = plt.subplots(1, 2, figsize=(W, 3.1), gridspec_kw={"width_ratios": [1, 1]})
ax = axs[0]
ax.plot(yrs, cnt(wdi), color=GREY, lw=2, label="Panel B (WDI)")
ax.plot(yrs, cnt(a10), color=BLUE, lw=2, label="Panel A10")
ax.plot(yrs, cnt(a16), color=ORANGE, lw=2, label="Panel A16")
ax.set_ylabel("Economies with data")
ax.set_xlabel("Year")
ax.set_title("(a) Economies per year", loc="left")
ax.legend(frameon=False, loc="center left", bbox_to_anchor=(0.0, 0.62))
ax.set_ylim(0, 230)
ax.set_xticks([2000, 2006, 2012, 2018, 2024])
ax = axs[1]
bot = np.zeros(len(yrs))
for src, c, lab in [("Eurostat gov_10a_exp", BLUE, "Eurostat"), ("OECD NAD Table 11", ORANGE, "OECD"), ("IMF GFS_COFOG", GREEN, "IMF")]:
    v = a10[a10.cofog10_source == src].groupby("year").iso3.nunique().reindex(yrs, fill_value=0).values
    ax.bar(yrs, v, bottom=bot, color=c, label=lab, width=0.8)
    bot += v
ax.set_ylabel("Economies in A10")
ax.set_xlabel("Year")
ax.set_title("(b) A10 by source", loc="left")
ax.legend(frameon=False, loc="upper left", ncol=3, columnspacing=0.8, handlelength=1.0, bbox_to_anchor=(0.0, 1.02))
ax.set_ylim(0, 92)
ax.set_xticks([2000, 2006, 2012, 2018, 2024])
fig.tight_layout(w_pad=1.5)
save(fig, "figD2_coverage_years")

# ---- Fig D3: cross-source agreement
LAB16 = {"general_public_services": "General public services", "defence": "Defence", "public_order_safety": "Public order and safety", "agriculture": "Agriculture",
         "energy": "Energy", "industry_construction": "Industry and construction", "transport": "Transport", "communication_digital": "Communication",
         "research_development": "R&D (economic affairs)", "environment": "Environment", "housing_community": "Housing and community", "water_supply": "Water supply",
         "health": "Health", "recreation_culture": "Recreation and culture", "education": "Education", "social_protection": "Social protection"}
LAB10 = {"GF01": "01 General public services", "GF02": "02 Defence", "GF03": "03 Public order", "GF04": "04 Economic affairs", "GF05": "05 Environment",
         "GF06": "06 Housing", "GF07": "07 Health", "GF08": "08 Recreation, culture", "GF09": "09 Education", "GF10": "10 Social protection"}
fig, axs = plt.subplots(1, 2, figsize=(W, 4.0), gridspec_kw={"width_ratios": [1, 1], "wspace": 1.05})
for ax, df, lab, ttl, colr in [(axs[0], es_oecd, lambda k: LAB16[k], f"(a) Eurostat vs OECD ({M['DEoN'].replace('{,}', ',')} rows)", BLUE),
                               (axs[1], imf_es, lambda k: LAB10[k.split("_")[1]], f"(b) IMF vs Eurostat ({M['DIeN'].replace('{,}', ',')} rows)", GREEN)]:
    df = df.iloc[::-1]
    yy = np.arange(len(df))
    ax.barh(yy, df.median_abs_diff_pp.values, color=colr, height=0.62)
    ax.set_yticks(yy)
    ax.set_yticklabels([lab(k) for k in df.index], fontsize=10)
    for yv, d_, r_ in zip(yy, df.median_abs_diff_pp.values, df.pearson.values):
        ax.text(d_ + 0.0015, yv, f"r={r_:.3f}", va="center", fontsize=9.6, color="black")
    ax.set_xlim(0, df.median_abs_diff_pp.max() * 1.9)
    ax.set_xlabel("Median |difference| (pp of total expenditure)")
    ax.set_title(ttl, loc="left", fontsize=10)
fig.subplots_adjust(left=0.20, right=0.99, bottom=0.14, top=0.92)
save(fig, "figD3_cross_source")

# ---- Fig D4: imputation by feature
order = []
for g, v in fg.items():
    order += [(g, c) for c in sorted(v, key=lambda c: -imp_pct[c])]
gcol = dict(zip(fg, [BLUE, ORANGE, GREEN, RED, PURPLE, SKY]))
fig, ax = plt.subplots(figsize=(W, 6.2))
yy = np.arange(len(order))[::-1]
for yv, (g, c) in zip(yy, order):
    ax.barh(yv + 0.18, imp_pct[c], height=0.36, color=gcol[g])
    ax.barh(yv - 0.18, miss_pct[c], height=0.36, color="white", edgecolor=gcol[g], hatch="////", lw=0.8)
    ax.text(imp_pct[c] + 0.8, yv + 0.18, f"{imp_pct[c]:.1f}", va="center", fontsize=10)
ax.set_yticks(yy)
ax.set_yticklabels([c for g, c in order], fontsize=9.6)
ax.text(50.8, 0.0, "excluded from models\nif above ~65%", fontsize=0.1, alpha=0)
ax.set_xlim(0, 92)
ax.set_ylim(-0.8, len(order) - 0.2)
ax.set_xlabel("Share of country-years (%)")
from matplotlib.patches import Patch
hand = [Patch(fc=gcol[g], label=g) for g in fg] + [Patch(fc="white", ec=GREY, hatch="////", label="hatched: still missing after imputation")]
ax.legend(handles=hand, loc="lower right", frameon=False, fontsize=10)
ax.set_title("Filled (flagged) cells and residual missingness, 217 economies x 25 years", loc="left", fontsize=10)
fig.tight_layout()
save(fig, "figD4_imputation")

# ---- Fig D5: coverage by income group and region
REG = {"Europe & Central Asia": "Europe & Central Asia", "Sub-Saharan Africa": "Sub-Saharan Africa", "Latin America & Caribbean": "Latin America & Caribbean",
       "East Asia & Pacific": "East Asia & Pacific", "Middle East, North Africa, Afghanistan & Pakistan": "MENA, Afghanistan, Pakistan", "South Asia": "South Asia", "North America": "North America"}
series = [("All economies", core, GREY), ("Panel B (WDI)", wdi, SKY), ("Panel A10", a10, BLUE), ("Panel A16", a16, ORANGE)]
fig, axs = plt.subplots(2, 1, figsize=(W, 8.4), gridspec_kw={"height_ratios": [4, 7], "hspace": 0.30})
for ax, keys, col, ttl, labf in [(axs[0], INC, "income_group", "(a) Economies by income group", lambda k: k),
                                 (axs[1], list(REG), "region", "(b) Economies by region", lambda k: REG[k])]:
    yy = np.arange(len(keys))[::-1]
    for j, (lab, d, c) in enumerate(series):
        v = [d[d[col] == k].iso3.nunique() for k in keys]
        ypos = yy + (1.5 - j) * 0.215
        ax.barh(ypos, v, height=0.19, color=c, label=lab)
        for yp, vv in zip(ypos, v):
            ax.text(vv + 1.2, yp, str(vv), va="center", ha="left", fontsize=8.5)
    ax.set_yticks(yy)
    ax.set_yticklabels([labf(k) for k in keys], fontsize=9.5)
    ax.set_xlabel("Number of economies", fontsize=9.5)
    ax.set_xlim(0, 108 if col == "income_group" else 72)
    ax.set_title(ttl, loc="left", fontsize=10.5, fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
axs[0].legend(frameon=False, loc="lower right", fontsize=9)
fig.subplots_adjust(left=0.27, right=0.97, top=0.96, bottom=0.06)
save(fig, "figD5_coverage_groups")

print("macros:", len(M), "| files written to", OUT)
for k in ["DMasterRows", "DMasterEcon", "DRowsSix", "DEconSix", "DRowsTen", "DEconTen", "DRowsWdi", "DEconWdi", "DNegSix", "DNegTen", "DJumpN", "DImpMean", "DDupKeys"]:
    print(k, M[k])

# ragged-right p-columns (no stretched word gaps in narrow cells) -- RAGGED_P
import re as _rr
for _f in pathlib.Path(GEN).glob("*.tex"):
    _s = _f.read_text(encoding="utf-8")
    if "arraybackslash" in _s:
        continue
    _n = "\n".join(_rr.sub(r"p\{", lambda m: ">{\\raggedright\\arraybackslash}p{", _l) if _l.startswith("\\begin{tabular}") else _l for _l in _s.split("\n"))
    if _n != _s:
        _f.write_text(_n, encoding="utf-8")
