"""Build GovAlloc-COFOG v1.0 (master panel) from RAW official sources + preserved legacy v1 dataset.

Inputs : data/raw/worldbank/*.json, data/raw/eurostat/*.json, legacy xlsx (v1, semi-synthetic)
Outputs: data/dataset_new/govalloc_cofog_master.csv        (all countries x years: features + targets + flags + legacy_* cols)
         data/dataset_new/govalloc_cofog_panel_a16.csv   (modelling panel A: Eurostat COFOG, 16 sectors)
         data/dataset_new/govalloc_cofog_panel_wdi.csv     (modelling panel B: global WDI, 4 sectors)
         data/dataset_old/govalloc_cofog_legacy_dataset.csv  (verbatim copy of the original dataset)
         data/dataset_new/govalloc_cofog_data_quality.json (coverage / imputation / legacy-vs-real audit)
Rules  : sector TARGETS are never imputed. FEATURES: (1) <=3-year linear interpolation inside a country series,
         (2) <=3-year edge fill, (3) region x income x year median. All imputed cells are flagged in
         `imp_*` columns and counted in `n_imputed_features`.
"""
import json, pathlib
import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW_WB, RAW_ES, OUT = ROOT / "data/raw/worldbank", ROOT / "data/raw/eurostat", ROOT / "data/dataset_new"
OUT.mkdir(parents=True, exist_ok=True)
LEGACY = ROOT / "data/dataset_old/original_sources/ML_Budget_Dataset_WorldBank_Completed.xlsx"
YEARS = range(2000, 2025)

from fetch_config import WB_IND, COFOG_CODES  # noqa: E402  (pipeline/fetch_config.py)

# ---------------- World Bank ----------------
meta = json.load(open(RAW_WB / "countries.json"))
cm = pd.DataFrame([{"iso3": c["id"], "iso2": c["iso2Code"], "country": c["name"], "region": c["region"]["value"],
                    "income_group": c["incomeLevel"]["value"], "is_agg": c["region"]["id"] == "NA"} for c in meta])
cm = cm[~cm.is_agg].drop(columns="is_agg")
frames = {}
for code, name in WB_IND.items():
    j = json.load(open(RAW_WB / f"{code}.json"))
    rows = [(r["countryiso3code"], int(r["date"]), r["value"]) for r in (j[1] or []) if r["value"] is not None]
    ser = pd.DataFrame(rows, columns=["iso3", "year", name]).set_index(["iso3", "year"])[name]
    frames[name] = ser[~ser.index.duplicated(keep="first")]
wb = pd.concat(frames, axis=1)
wb = wb[wb.index.get_level_values("iso3").isin(cm.iso3)]
grid = pd.MultiIndex.from_product([sorted(cm.iso3), YEARS], names=["iso3", "year"])
wb = wb.reindex(grid).reset_index().merge(cm, on="iso3", how="left")

# ---------------- Eurostat COFOG ----------------
def es_read(unit, code):
    j = json.load(open(RAW_ES / f"{unit}_{code}.json"))
    geos = list(j["dimension"]["geo"]["category"]["index"])
    times = list(j["dimension"]["time"]["category"]["index"])
    nt = len(times)
    out = [(geos[int(k) // nt], int(times[int(k) % nt]), v) for k, v in j["value"].items()]
    d = pd.DataFrame(out, columns=["geo", "year", f"{unit}_{code}"])
    return d.set_index(["geo", "year"])[f"{unit}_{code}"]

es = pd.concat({f"{u}_{c}": es_read(u, c) for u in ["PC_GDP", "PC_TOT", "MIO_EUR"] for c in COFOG_CODES}, axis=1)
es = es[~es.index.get_level_values("geo").str.startswith(("EU", "EA"))]
es = es.reset_index()
es["iso2"] = es.geo.replace({"EL": "GR"})
es = es.merge(cm[["iso2", "iso3"]], on="iso2", how="inner").drop(columns=["geo", "iso2"])
es = es[es.year.between(2000, 2024)].reset_index(drop=True)

SECT = {  # sector -> COFOG codes (COFOG-aligned functional taxonomy, 16 sectors)
    "general_public_services": ["GF01"], "defence": ["GF02"], "public_order_safety": ["GF03"],
    "agriculture": ["GF0402"], "energy": ["GF0403"], "industry_construction": ["GF0404", "GF0407"],
    "transport": ["GF0405"], "communication_digital": ["GF0406"], "research_development": ["GF0408"],
    "environment": ["GF05"], "housing_community": ["GF06", "-GF0603"], "water_supply": ["GF0603"],
    "health": ["GF07"], "recreation_culture": ["GF08"], "education": ["GF09"], "social_protection": ["GF10"],
}
cof = es[["iso3", "year"]].copy()
for unit, suf in [("PC_GDP", "pct_gdp"), ("PC_TOT", "pct_total"), ("MIO_EUR", "mio_eur")]:
    for s, parts in SECT.items():
        acc = None
        for p in parts:
            sign = -1 if p.startswith("-") else 1
            v = es[f"{unit}_{p.lstrip('-')}"] * sign
            acc = v if acc is None else acc + v          # NaN propagates: no partial sums
        cof[f"cofog_{s}_{suf}"] = acc.values
cof["cofog_total_expenditure_pct_gdp"] = es["PC_GDP_TOTAL"].values
cof["cofog_total_expenditure_mio_eur"] = es["MIO_EUR_TOTAL"].values
sec_cols = [f"cofog_{s}_pct_total" for s in SECT]
cof["cofog_other_residual_pct_total"] = 100 - cof[sec_cols].sum(axis=1, min_count=len(sec_cols))
cof["cofog_complete_flag"] = cof[sec_cols].notna().all(axis=1).astype(int)

cof["cofog_source_name"] = "Eurostat gov_10a_exp"

# ---- OECD NAD Table 11 (COFOG) for non-Eurostat economies (AUS, CHL, COL, CRI, GBR, ISR, JPN, KOR, USA); shares only ----
oe = pd.read_csv(ROOT / "data/raw/oecd/oecd_table11_S13_OTE.csv", low_memory=False)
oe = oe[(oe.CONSOLIDATION == "P") & oe.EXPENDITURE.isin(COFOG_CODES + [f"GF{i:02d}" for i in range(1, 11)])]
oe = oe.drop_duplicates(["REF_AREA", "TIME_PERIOD", "EXPENDITURE"])
ow = oe.pivot(index=["REF_AREA", "TIME_PERIOD"], columns="EXPENDITURE", values="OBS_VALUE")
ow["TOTAL_L1"] = ow[[f"GF{i:02d}" for i in range(1, 11)]].sum(axis=1, min_count=10)
def oecd_share(parts):
    acc = None
    for q in parts:
        sign = -1 if q.startswith("-") else 1
        v = ow[q.lstrip("-")] * sign
        acc = v if acc is None else acc + v
    return acc / ow["TOTAL_L1"] * 100
oc = pd.DataFrame({f"cofog_{s}_pct_total": oecd_share(parts) for s, parts in SECT.items()}).reset_index()
oc = oc.rename(columns={"REF_AREA": "iso3", "TIME_PERIOD": "year"})
oc = oc[oc.year.between(2000, 2024)]
# cross-source validation on overlap (Eurostat vs OECD), reported in the data-quality json
ov = cof.merge(oc, on=["iso3", "year"], suffixes=("_es", "_oe"))
xs_val = {}
for s in SECT:
    a, b = ov[f"cofog_{s}_pct_total_es"], ov[f"cofog_{s}_pct_total_oe"]
    m = a.notna() & b.notna()
    if m.sum():
        xs_val[s] = {"n": int(m.sum()), "median_abs_diff_pp": float((a[m] - b[m]).abs().median()), "pearson": float(np.corrcoef(a[m], b[m])[0, 1])}
new_iso = sorted(set(oc.iso3) - set(cof.iso3) - {"EA20", "EU", "EU27_2020"})
oc = oc[oc.iso3.isin(new_iso)].copy()
oc["cofog_source_name"] = "OECD NAD Table 11"
oc["cofog_other_residual_pct_total"] = 100 - oc[sec_cols].sum(axis=1, min_count=len(sec_cols))
oc["cofog_complete_flag"] = oc[sec_cols].notna().all(axis=1).astype(int)
print("OECD-only countries:", new_iso, "rows complete:", int(oc.cofog_complete_flag.sum()))
cof = pd.concat([cof, oc], ignore_index=True)
# ---- 10-division COFOG (level 1) from Eurostat + OECD + IMF: wide-coverage panel A10 (priority Eurostat > OECD > IMF) ----
DIV = [f"GF{i:02d}" for i in range(1, 11)]
D10 = [f"cofog10_{g}_pct_total" for g in DIV]
a_es = es[["iso3", "year"]].copy()
for g in DIV:
    a_es[f"cofog10_{g}_pct_total"] = es[f"PC_TOT_{g}"].values
a_es["cofog10_source"] = "Eurostat gov_10a_exp"
a_oe = (ow[DIV].div(ow["TOTAL_L1"], axis=0) * 100).reset_index().rename(columns={"REF_AREA": "iso3", "TIME_PERIOD": "year"})
a_oe.columns = ["iso3", "year"] + D10
a_oe["cofog10_source"] = "OECD NAD Table 11"
imf_path = ROOT / "data/raw/imf/imf_gfs_cofog_S13_POTO.csv"
a_im = pd.DataFrame(columns=["iso3", "year"] + D10 + ["cofog10_source"])
xs10 = {}
if imf_path.exists():
    im = pd.read_csv(imf_path, low_memory=False)
    im = im[im.COFOG.isin(DIV)].drop_duplicates(["COUNTRY", "TIME_PERIOD", "COFOG"])
    iw = im.pivot(index=["COUNTRY", "TIME_PERIOD"], columns="COFOG", values="OBS_VALUE").reset_index()
    iw = iw.rename(columns={"COUNTRY": "iso3", "TIME_PERIOD": "year"})
    iw = iw.dropna(subset=DIV)
    iw["imf_raw_sum"] = iw[DIV].sum(axis=1)
    iw = iw[(iw.imf_raw_sum > 97) & (iw.imf_raw_sum < 103)]            # internally consistent general-government breakdowns only
    for g in DIV:
        iw[g] = iw[g] / iw.imf_raw_sum * 100
    a_im = iw[["iso3", "year"] + DIV].copy()
    a_im.columns = ["iso3", "year"] + D10
    a_im["cofog10_source"] = "IMF GFS_COFOG"
    ov = a_es.merge(a_im, on=["iso3", "year"], suffixes=("_a", "_b"))
    for g in D10:
        m = ov[[g + "_a", g + "_b"]].dropna()
        if len(m) > 3:
            xs10[g] = {"n": int(len(m)), "median_abs_diff_pp": float((m[g + "_a"] - m[g + "_b"]).abs().median()), "pearson": float(np.corrcoef(m[g + "_a"], m[g + "_b"])[0, 1])}
a10 = pd.concat([a_es, a_oe, a_im], ignore_index=True)
a10 = a10[a10.year.between(2000, 2024)].dropna(subset=D10)
a10["_prio"] = a10.cofog10_source.map({"Eurostat gov_10a_exp": 0, "OECD NAD Table 11": 1, "IMF GFS_COFOG": 2})
a10 = a10.sort_values(["iso3", "year", "_prio"]).drop_duplicates(["iso3", "year"]).drop(columns="_prio")
a10["cofog10_complete_flag"] = 1
iso_ok = set(cm.iso3) | {"TWN"}
a10 = a10[a10.iso3.isin(iso_ok)]
print("A10 rows", len(a10), "economies", a10.iso3.nunique(), a10.cofog10_source.value_counts().to_dict())

df = wb.merge(cof, on=["iso3", "year"], how="left")
df = df.merge(a10, on=["iso3", "year"], how="left")
df["cofog10_complete_flag"] = df["cofog10_complete_flag"].fillna(0).astype(int)
ren = {"T_edu_pct_gdp": "wdi_education_pct_gdp", "T_edu_pct_govexp": "wdi_education_pct_govexp",
       "T_health_pct_gdp": "wdi_health_pct_gdp", "T_health_pct_govexp": "wdi_health_pct_govexp",
       "T_defence_pct_gdp": "wdi_defence_pct_gdp", "T_defence_pct_govexp": "wdi_defence_pct_govexp",
       "T_rnd_pct_gdp": "wdi_rnd_pct_gdp"}
df = df.rename(columns=ren)

# ---------------- Feature imputation (flagged) ----------------
FEATS = [v for v in WB_IND.values() if not v.startswith("T_")]
df = df.sort_values(["iso3", "year"]).reset_index(drop=True)
imp_total = pd.Series(0, index=df.index)
for f in FEATS:
    orig = df[f].copy()
    interp = df.groupby("iso3")[f].transform(lambda s: s.interpolate(limit=3, limit_area="inside"))
    edge = interp.groupby(df.iso3).transform(lambda s: s.ffill(limit=3).bfill(limit=3))
    grp = df.assign(_v=edge).groupby(["region", "income_group", "year"])["_v"].transform("median")
    filled = edge.fillna(grp)
    flag = orig.isna() & filled.notna()
    df[f"imp_{f}"] = flag.astype(np.int8)
    df[f] = filled
    imp_total += flag.astype(int)
df["n_imputed_features"] = imp_total
df["log_gdp"] = np.log10(df.gdp_usd)
df["log_pop"] = np.log10(df.population)
for s in SECT:   # derived USD estimates (share of GDP x WDI nominal GDP): flagged as derived
    df[f"cofog_{s}_usd_derived"] = df[f"cofog_{s}_pct_gdp"] / 100 * df["gdp_usd"]

# ---------------- Legacy v1 (preserved verbatim) ----------------
leg = pd.read_excel(LEGACY, sheet_name="Completed_Dataset")
leg.to_csv(ROOT / "data/dataset_old/govalloc_cofog_legacy_dataset.csv", index=False)
leg2 = leg.rename(columns={"country_iso3": "iso3"}).drop(columns=["country"])
print("legacy iso3 not in WB:", sorted(set(leg2.iso3) - set(cm.iso3)))
leg2 = leg2.add_prefix("legacy_").rename(columns={"legacy_iso3": "iso3", "legacy_year": "year"})
orphan = leg2[~leg2.iso3.isin(cm.iso3)].copy()          # e.g. Taiwan: not a World Bank economy -> keep legacy-only rows
df = df.merge(leg2, on=["iso3", "year"], how="left")
df["has_legacy_v1_row"] = df["legacy_gdp_usd"].notna().astype(int)
if len(orphan):
    orphan["country"] = orphan.iso3.map({"TWN": "Taiwan"}).fillna(orphan.iso3)
    orphan["region"], orphan["income_group"] = "East Asia & Pacific", "High income"
    orphan["has_legacy_v1_row"] = 1; orphan["legacy_only_row"] = 1
    df = pd.concat([df, orphan], ignore_index=True)
df["legacy_only_row"] = df.get("legacy_only_row", 0)
df["legacy_only_row"] = df["legacy_only_row"].fillna(0).astype(int)

# ---------------- Provenance ----------------
wdi_t = [c for c in df if c.startswith("wdi_") and c.endswith(("pct_gdp", "pct_govexp"))]
df["wdi_target_n"] = df[wdi_t].notna().sum(axis=1)
df["cofog_source"] = np.where(df.cofog_complete_flag.fillna(0) == 1, df.cofog_source_name, "")
order = ["iso3", "iso2", "country", "region", "income_group", "year"]
df = df[order + [c for c in df.columns if c not in order]]
df.to_csv(OUT / "govalloc_cofog_master.csv", index=False)

df["cofog_complete_flag"] = df["cofog_complete_flag"].fillna(0).astype(int)
df["wdi_target_n"] = df["wdi_target_n"].fillna(0).astype(int)
pa = df[df.cofog_complete_flag == 1].copy()
pa.to_csv(OUT / "govalloc_cofog_panel_a16.csv", index=False)
pb = df[df.wdi_target_n >= 1].copy()
pb.to_csv(OUT / "govalloc_cofog_panel_wdi.csv", index=False)
p10 = df[df.cofog10_complete_flag == 1].copy()
p10.to_csv(OUT / "govalloc_cofog_panel_a10.csv", index=False)

# ---------------- Audit: legacy vs real ----------------
aud = {"master_rows": len(df), "master_cols": df.shape[1], "countries": int(df.iso3.nunique()),
       "cofog_panel_rows": len(pa), "cofog_panel_countries": int(pa.iso3.nunique()),
       "wdi_panel_rows": len(pb), "wdi_panel_countries": int(pb.iso3.nunique()),
       "cofog10_panel_rows": len(p10), "cofog10_panel_countries": int(p10.iso3.nunique()), "cofog10_by_source": p10.cofog10_source.value_counts().to_dict(),
       "cofog10_imf_vs_eurostat": xs10,
       "legacy_rows_preserved": int(df.has_legacy_v1_row.sum()), "legacy_vs_real": {}}
cmp = df[df.has_legacy_v1_row == 1]
pairs = {"gdp_usd": "legacy_gdp_usd", "population": "legacy_population", "life_expectancy": "legacy_life_expectancy_years",
         "inflation_pct": "legacy_inflation_percent", "gdp_growth_pct": "legacy_gdp_growth_percent",
         "unemployment_pct": "legacy_unemployment_rate_percent", "internet_users_pct": "legacy_internet_users_percent"}
for r, l in pairs.items():
    m = cmp[[r, l]].dropna()
    rel = (m[l] - m[r]).abs() / m[r].abs().clip(lower=1e-9)
    aud["legacy_vs_real"][r] = {"n": int(len(m)), "median_abs_rel_err": float(rel.median()),
                                "p90_abs_rel_err": float(rel.quantile(.9)), "pearson": float(np.corrcoef(m[r], m[l])[0, 1])}
m = cmp.assign(leg_def=cmp.legacy_defence_usd / cmp.legacy_gdp_usd * 100, leg_edu=cmp.legacy_education_usd / cmp.legacy_gdp_usd * 100,
               leg_hlt=cmp.legacy_healthcare_usd / cmp.legacy_gdp_usd * 100)
for leg_c, w in [("leg_def", "wdi_defence_pct_gdp"), ("leg_edu", "wdi_education_pct_gdp"), ("leg_hlt", "wdi_health_pct_gdp")]:
    q = m[[leg_c, w]].dropna()
    aud["legacy_vs_real"][f"{leg_c}_vs_{w}"] = {"n": int(len(q)), "median_abs_err_pp": float((q[leg_c] - q[w]).abs().median()),
                                                "pearson": float(np.corrcoef(q[leg_c], q[w])[0, 1])}
aud["feature_missing_after_imputation_pct"] = {f: round(float(df[f].isna().mean() * 100), 1) for f in FEATS}
aud["feature_imputed_cells_pct"] = {f: round(float(df[f"imp_{f}"].mean() * 100), 1) for f in FEATS}
aud["eurostat_vs_oecd_crosscheck"] = xs_val
aud["oecd_added_countries"] = new_iso
aud["cofog_target_years"] = [int(pa.year.min()), int(pa.year.max())]
json.dump(aud, open(OUT / "govalloc_cofog_data_quality.json", "w"), indent=1)
print(json.dumps(aud, indent=1)[:6000])
