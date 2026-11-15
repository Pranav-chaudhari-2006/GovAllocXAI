"""Institutional features from the three manually downloaded sources (data/raw/institutional):
  * IMF Fiscal Rules Dataset 1985-2024 (rule types in place)           -> fr_*
  * Database of Political Institutions 2020 (election years, term left) -> dpi_*
  * IMF MONA arrangements (programme active in a year)                  -> imf_prog_*
Ablation on A10 (xgb): base vs base + each group vs base + all; cold-start leave-country-out (6 folds, seeds 0-2) and annual delta-xgb (train<=2019, test 2020-24).
Outputs data/dataset_new/govalloc_cofog_institutional_manual.csv, results/18_institutional_features/manual_*.csv|json
"""
import glob
import importlib.util
import json
import os
import pathlib
import re
import sys
import unicodedata

os.environ.setdefault("OMP_NUM_THREADS", "4")
import numpy as np
import pandas as pd

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
from gov_common import *  # noqa: F401,F403

spec = importlib.util.spec_from_file_location("arch21", HERE / "06_stack_architecture.py")
arch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(arch)

RAW = pathlib.Path(__file__).resolve().parent.parent / "data" / "raw" / "institutional"
master = pd.read_csv(PROC / "govalloc_cofog_master.csv", usecols=["iso3", "country"]).drop_duplicates("iso3")


def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\(.*?\)", " ", s)
    s = re.sub(r"[^a-z ]", " ", s)
    s = re.sub(r"\b(the|of|republic|islamic|federal|democratic|peoples|kingdom|state|states|rep)\b", " ", s)
    return " ".join(s.split())


ALIAS = {"russia": "RUS", "korea": "KOR", "south korea": "KOR", "slovak": "SVK", "slovakia": "SVK", "czech": "CZE", "czechia": "CZE", "turkiye": "TUR", "turkey": "TUR",
         "egypt arab": "EGY", "egypt": "EGY", "iran": "IRN", "kyrgyz": "KGZ", "congo dem": "COD", "congo": "COG", "cote d ivoire": "CIV", "gambia": "GMB", "bahamas": "BHS",
         "yemen": "YEM", "venezuela": "VEN", "lao": "LAO", "laos": "LAO", "syrian arab": "SYR", "syria": "SYR", "macedonia": "MKD", "north macedonia": "MKD", "fyr macedonia": "MKD",
         "hong kong": "HKG", "vietnam": "VNM", "viet nam": "VNM", "moldova": "MDA", "burma": "MMR", "myanmar": "MMR", "swaziland": "SWZ", "eswatini": "SWZ",
         "cape verde": "CPV", "cabo verde": "CPV", "timor leste": "TLS", "east timor": "TLS", "west bank gaza": "PSE", "kosovo": "XKX", "sao tome principe": "STP",
         "st lucia": "LCA", "st kitts nevis": "KNA", "st vincent grenadines": "VCT", "bosnia herzegovina": "BIH", "brunei darussalam": "BRN", "brunei": "BRN",
         "china people s": "CHN", "china p r mainland": "CHN", "china": "CHN", "unified germany": "DEU", "germany": "DEU", "germany west": "DEU", "slovenia": "SVN"}
BYNAME = {norm(r.country): r.iso3 for r in master.itertuples()}
BYNAME.update(ALIAS)
ISO = set(master.iso3)


def to_iso(name, code=None):
    if code is not None and isinstance(code, str) and code in ISO:
        return code
    n = norm(name)
    if n in BYNAME:
        return BYNAME[n]
    n2 = norm(str(name).split(",")[0])
    return BYNAME.get(n2)


# ---------------- fiscal rules ----------------
fr = pd.read_excel(RAW / "imf_fiscal_rules_1985_2024.xlsx", sheet_name="Rules", header=1).iloc[2:]
fr = fr[pd.to_numeric(fr["year"], errors="coerce").notna()].copy()
fr["year"] = fr["year"].astype(int)
fr["iso3"] = [to_iso(n) for n in fr["Country name"]]
unm_fr = sorted(set(fr.loc[fr.iso3.isna(), "Country name"].astype(str)))
for c, n in [("ER: Expenditure rule", "fr_expenditure_rule"), ("RR: Revenue rule", "fr_revenue_rule"), ("BBR: Budget balance rule", "fr_balance_rule"), ("DR: Debt rule", "fr_debt_rule")]:
    fr[n] = (fr[c].astype(str).str.strip() == "1").astype(float)
fr["fr_n_rules"] = fr[["fr_expenditure_rule", "fr_revenue_rule", "fr_balance_rule", "fr_debt_rule"]].sum(1)
FR = [c for c in fr.columns if c.startswith("fr_")]
fr = fr.dropna(subset=["iso3"]).groupby(["iso3", "year"], as_index=False)[FR].max()

# ---------------- DPI ----------------
dp = pd.read_csv(RAW / "dpi2020.csv", low_memory=False)
dp["iso3"] = [to_iso(n, str(c)) for n, c in zip(dp.countryname, dp.ifs)]
unm_dp = sorted(set(dp.loc[dp.iso3.isna(), "countryname"].astype(str)))
for c in ["legelec", "exelec", "yrcurnt"]:
    dp[c] = pd.to_numeric(dp[c], errors="coerce").replace(-999, np.nan)
dp["dpi_election_year"] = ((dp.legelec == 1) | (dp.exelec == 1)).astype(float).where(dp.legelec.notna() | dp.exelec.notna())
dp["dpi_years_to_election"] = dp.yrcurnt
DP = ["dpi_election_year", "dpi_years_to_election"]
dp = dp.dropna(subset=["iso3"]).groupby(["iso3", "year"], as_index=False)[DP].max()

# ---------------- MONA ----------------
mo = pd.read_excel(RAW / "imf_mona_program.xlsx")
mo["iso3"] = [to_iso(n) for n in mo["Country Name"]]
unm_mo = sorted(set(mo.loc[mo.iso3.isna(), "Country Name"].astype(str)))
mo = mo.dropna(subset=["iso3"]).drop_duplicates(["Arrangement Number", "iso3"])
rows = []
for r in mo.to_dict("records"):
    a = r["Approval Year"]
    ends = [pd.to_datetime(r["Initial End Date"], errors="coerce", format="mixed"), pd.to_datetime(r["Revised End Date"], errors="coerce", format="mixed")]
    e = max([x for x in ends if pd.notna(x)], default=None)
    if pd.isna(a) or e is None:
        continue
    for y in range(int(a), e.year + 1):
        rows.append((r["iso3"], y, 1.0))
mo_y = pd.DataFrame(rows, columns=["iso3", "year", "imf_prog_active"]).groupby(["iso3", "year"], as_index=False).max()
MO = ["imf_prog_active"]

inst = fr.merge(dp, on=["iso3", "year"], how="outer").merge(mo_y, on=["iso3", "year"], how="outer")
inst.to_csv(PROC / "govalloc_cofog_institutional_manual.csv", index=False)

out = {"unmatched": {"fiscal_rules": unm_fr, "dpi": unm_dp, "mona": unm_mo}}
d, T = arch.load_panel("A10")
d = d.reset_index(drop=True).merge(inst, on=["iso3", "year"], how="left")
# MONA covers every year with no arrangement -> 0 for covered economies (all MONA history is complete); others stay NaN only if absent from MONA
d["imf_prog_active"] = d["imf_prog_active"].fillna(0.0).where(d.year <= 2024, np.nan)
# fiscal-rule flags: NaN where the economy is not in the dataset (not 'no rule')
GROUPS = {"fiscal_rules": FR, "dpi_elections": DP, "imf_programmes": MO}
out["coverage_A10"] = {c: float(d[c].notna().mean()) for c in FR + DP + MO}
print("coverage", out["coverage_A10"], flush=True)
SPECS = [("base", FEATURES)] + [(k, FEATURES + v) for k, v in GROUPS.items()] + [("all_institutional", FEATURES + FR + DP + MO)]

Y = d[T]
cs = {}
res = {}
SEEDS = [0, 1, 2]
for seed in SEEDS:
    ctry = d.iso3.unique(); perm = np.random.default_rng(seed).permutation(len(ctry))
    fold = d.iso3.map({c: i % 6 for i, c in zip(range(len(ctry)), ctry[perm])}).values
    for name, cols in SPECS:
        oof = np.zeros((len(d), len(T)))
        for f in range(6):
            a, b = np.where(fold != f)[0], np.where(fold == f)[0]
            oof[b] = arch.fit_predict_multi("xgb", d.iloc[a][cols], Y.iloc[a], d.iloc[b][cols], 42 + seed).values
        res[(seed, name)] = tvd(simplex_renorm(oof), Y.values)
    print("seed", seed, "done", flush=True)
for name, _ in SPECS[1:]:
    gains = np.mean([res[(s, "base")] - res[(s, name)] for s in SEEDS], axis=0)
    lo, hi = boot_ci(gains, d.iso3.values)
    cs[name] = {"TVD_base": float(np.mean([res[(s, "base")].mean() for s in SEEDS])), "TVD_spec": float(np.mean([res[(s, name)].mean() for s in SEEDS])), "gain": float(gains.mean()), "ci95": [lo, hi]}
out["cold_start"] = cs
print(cs, flush=True)

ok = d.has_lag
tr, te = d[ok & (d.year <= 2019)], d[ok & (d.year >= 2020)]
L1, L1te = tr[[f"h1_{t}" for t in T]].values, te[[f"h1_{t}" for t in T]].values
tv = {}
for name, cols in SPECS:
    X1 = cols + [f"h1_{t}" for t in T]
    D = arch.fit_predict_multi("xgb", tr[X1], pd.DataFrame(tr[T].values - L1, columns=T, index=tr.index), te[X1]).values
    tv[name] = tvd(simplex_renorm(L1te + D), te[T].values)
out["annual"] = {}
for name, _ in SPECS[1:]:
    gain = tv["base"] - tv[name]
    lo, hi = boot_ci(gain, te.iso3.values)
    out["annual"][name] = {"n": int(len(te)), "TVD_base": float(tv["base"].mean()), "TVD_spec": float(tv[name].mean()), "gain": float(gain.mean()), "ci95": [lo, hi]}
print(out["annual"], flush=True)
json.dump(out, open(RES / "18_institutional_features/manual_summary.json", "w"), indent=1, default=float)
pd.DataFrame([{"regime": "cold-start", "spec": k, **v} for k, v in cs.items()] + [{"regime": "annual", "spec": k, **v} for k, v in out["annual"].items()]).to_csv(RES / "18_institutional_features/manual_ablation.csv", index=False)
print("done")
