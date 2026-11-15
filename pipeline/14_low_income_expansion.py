"""Low-income coverage expansion for the 10-division COFOG panel (A10) + cold-start evaluation by income group.

(a) Diagnose why low / lower-middle income economies are missing from A10 (IMF S13 raw files).
(b) Download IMF GFS_COFOG central-government (S1311) series (same call pattern as 01b), store raw in data/raw/imf_extra/,
    admit extra rows with a relaxed consistency window (raw sum 90-110, renormalised to 100) and FLAG them:
      cofog10_scope  = 'general government' | 'central government'
      cofog10_strict = 1 if raw sum in (97,103) and general government (i.e. same standard as A10), else 0
    -> data/dataset_new/govallocxai_new_cofog10x_panel.csv  (A10 rows + admitted rows; A10 is untouched)
(c) Leave-country-out cold start (6 folds x seeds 0,1) by income group: peer mean, XGBoost, XGBoost + inverse-frequency
    income-group sample weights, XGBoost + income-group one-hot; on the expanded panel and on the original A10 rows only.
Outputs: results/10_low_income_expansion/*.csv, results/10_low_income_expansion/summary.json
"""
import os
os.environ["OMP_NUM_THREADS"] = "4"
import io
import json
import pathlib
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
import requests

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from gov_common import *  # noqa: F401,F403

RAW = ROOT / "data/raw/imf"
EXTRA = ROOT / "data/raw/imf_extra"
URL = "https://api.imf.org/external/sdmx/2.1/data/IMF.STA,GFS_COFOG/{c}.{s}.G2MF.*.POTO_PT?startPeriod=2000"
KEEP = ["COUNTRY", "SECTOR", "COFOG", "TIME_PERIOD", "OBS_VALUE", "STATUS"]
DIV = [f"GF{i:02d}" for i in range(1, 11)]
D10 = [f"cofog10_{g}_pct_total" for g in DIV]
LOW = ["Low income", "Lower middle income"]
SUMMARY = {}

master = pd.read_csv(PROC / "govallocxai_new_master.csv", low_memory=False)
a10 = pd.read_csv(PROC / "govallocxai_new_cofog10_panel.csv")
inc = master.groupby("iso3").income_group.first()
low_iso = sorted(inc[inc.isin(LOW)].index)

# ------------------------------------------------------------------ (a) diagnosis of the S13 raw files
rows = []
for c in low_iso:
    f = RAW / "by_country" / f"{c}.csv"
    r = {"iso3": c, "income_group": inc[c], "file_exists": f.exists() and f.stat().st_size > 5}
    if r["file_exists"]:
        d = pd.read_csv(f)
        d = d[d.COFOG.isin(DIV)].dropna(subset=["OBS_VALUE"]).drop_duplicates(["TIME_PERIOD", "COFOG"])
        r["n_obs_div"] = len(d)
        r["years_any_div"] = int(d.TIME_PERIOD.nunique())
        r["max_divs_in_a_year"] = int(d.groupby("TIME_PERIOD").COFOG.nunique().max()) if len(d) else 0
        w = d.pivot(index="TIME_PERIOD", columns="COFOG", values="OBS_VALUE")
        w = w.reindex(columns=DIV)
        full = w.dropna(subset=DIV)
        r["years_all10"] = len(full)
        s = full[DIV].sum(axis=1)
        r["years_all10_sum97_103"] = int(((s > 97) & (s < 103)).sum())
        r["years_all10_sum90_110"] = int(((s > 90) & (s < 110)).sum())
        r["n_divisions_ever"] = int(d.COFOG.nunique())
    else:
        r.update({"n_obs_div": 0, "years_any_div": 0, "max_divs_in_a_year": 0, "years_all10": 0, "years_all10_sum97_103": 0,
                  "years_all10_sum90_110": 0, "n_divisions_ever": 0})
    r["in_A10"] = c in set(a10.iso3)
    rows.append(r)
diag = pd.DataFrame(rows)


def reason(r):
    if r.in_A10:
        return "in A10"
    if r.n_obs_div == 0:
        return "no S13 COFOG data at all"
    if r.years_all10 == 0:
        return "S13 data exist but never all 10 divisions in one year"
    if r.years_all10_sum97_103 == 0:
        return "all-10 years exist but raw sum outside 97-103"
    return "other"


diag["reason_missing"] = diag.apply(reason, axis=1)
diag.to_csv(RES / "10_low_income_expansion/diagnosis_S13.csv", index=False)
SUMMARY["diagnosis"] = {g: diag[diag.income_group == g].reason_missing.value_counts().to_dict() for g in LOW}
SUMMARY["diagnosis"]["n_economies"] = {g: int((diag.income_group == g).sum()) for g in LOW}
print(diag.groupby(["income_group", "reason_missing"]).size())

# ------------------------------------------------------------------ (b) download S1311 for low / lower-middle income economies
for s in ["S1311"]:
    (EXTRA / s).mkdir(parents=True, exist_ok=True)


def job(args):
    c, s = args
    f = EXTRA / s / f"{c}.csv"
    if f.exists():
        return c, s, "cached"
    for i in range(4):
        try:
            r = requests.get(URL.format(c=c, s=s), headers={"Accept": "application/vnd.sdmx.data+csv"}, timeout=90)
            if r.status_code == 404 or (r.status_code == 200 and len(r.content) < 300):
                f.write_text("")
                return c, s, "empty"
            r.raise_for_status()
            d = pd.read_csv(io.BytesIO(r.content), usecols=lambda x: x in KEEP, low_memory=False)
            d.to_csv(f, index=False)
            return c, s, f"ok {len(d)}"
        except Exception:  # noqa: BLE001
            time.sleep(2 * (i + 1))
    return c, s, "FAIL"


with ThreadPoolExecutor(3) as ex:
    res = list(ex.map(job, [(c, "S1311") for c in low_iso]))
print({k: sum(1 for *_, st in res if st.startswith(k)) for k in ["ok", "empty", "cached", "FAIL"]}, flush=True)
SUMMARY["download_S1311"] = {k: sum(1 for *_, st in res if st.startswith(k)) for k in ["ok", "empty", "cached", "FAIL"]}


def wide(df, scope):
    d = df[df.COFOG.isin(DIV)].dropna(subset=["OBS_VALUE"]).drop_duplicates(["COUNTRY", "TIME_PERIOD", "COFOG"])
    w = d.pivot(index=["COUNTRY", "TIME_PERIOD"], columns="COFOG", values="OBS_VALUE").reset_index()
    w = w.rename(columns={"COUNTRY": "iso3", "TIME_PERIOD": "year"})
    for g in DIV:
        if g not in w:
            w[g] = np.nan
    w = w.dropna(subset=DIV)
    w["raw_sum"] = w[DIV].sum(axis=1)
    w["cofog10_scope"] = scope
    w["year"] = w.year.astype(int)
    return w


# general-government rows (S13) for the low/lower-middle economies, relaxed window
s13 = pd.concat([pd.read_csv(RAW / "by_country" / f"{c}.csv") for c in low_iso
                 if (RAW / "by_country" / f"{c}.csv").stat().st_size > 5], ignore_index=True)
w13 = wide(s13, "general government")
parts = [pd.read_csv(f) for f in sorted((EXTRA / "S1311").glob("*.csv")) if f.stat().st_size > 5]
w11 = wide(pd.concat(parts, ignore_index=True), "central government") if parts else pd.DataFrame()
SUMMARY["candidate_rows"] = {"S13_all10": len(w13), "S1311_all10": len(w11)}
cand = pd.concat([w13, w11], ignore_index=True)
cand = cand[(cand.raw_sum > 90) & (cand.raw_sum < 110) & cand.year.between(2000, 2024)]
cand["_p"] = cand.cofog10_scope.map({"general government": 0, "central government": 1})
cand = cand.sort_values(["iso3", "year", "_p"]).drop_duplicates(["iso3", "year"])
cand = cand.merge(a10[["iso3", "year"]].assign(_in=1), on=["iso3", "year"], how="left")
cand = cand[cand._in.isna()].drop(columns=["_in", "_p"])
for g in DIV:
    cand[g] = cand[g] / cand.raw_sum * 100
cand["cofog10_strict"] = ((cand.cofog10_scope == "general government") & (cand.raw_sum > 97) & (cand.raw_sum < 103)).astype(int)
cand = cand.rename(columns={g: f"cofog10_{g}_pct_total" for g in DIV})
cand["cofog10_source"] = np.where(cand.cofog10_scope == "general government", "IMF GFS_COFOG S13 (relaxed 90-110)", "IMF GFS_COFOG S1311 (central gov., 90-110)")
# attach features from the master by iso3/year (same columns as the A10 panel)
feat_cols = [c for c in a10.columns if c not in D10 + ["cofog10_source", "cofog10_complete_flag"]]
new = cand.merge(master[feat_cols], on=["iso3", "year"], how="inner")
new["cofog10_complete_flag"] = 1
dropped = len(cand) - len(new)
base = a10.copy()
base["cofog10_scope"], base["cofog10_strict"], base["imf_raw_sum"] = "general government", 1, np.nan
new["imf_raw_sum"] = new["raw_sum"]
new = new[[c for c in base.columns if c in new.columns]]
x = pd.concat([base, new], ignore_index=True).sort_values(["iso3", "year"]).reset_index(drop=True)
x["is_original_a10"] = x.index.map(lambda i: 0)
key = set(zip(a10.iso3, a10.year))
x["is_original_a10"] = [int((i, y) in key) for i, y in zip(x.iso3, x.year)]
x.to_csv(PROC / "govallocxai_new_cofog10x_panel.csv", index=False)
print("cand dropped (no master row):", dropped)


def cov(df):
    t = df.groupby("income_group").agg(economies=("iso3", "nunique"), rows=("iso3", "size")).reindex(["Low income", "Lower middle income", "Upper middle income", "High income"])
    return t


cnt = pd.concat({"A10": cov(x[x.is_original_a10 == 1]),
                 "expanded_all": cov(x),
                 "new_rows_all": cov(x[x.is_original_a10 == 0]),
                 "new_general_gov": cov(x[(x.is_original_a10 == 0) & (x.cofog10_scope == "general government")]),
                 "new_central_gov": cov(x[(x.is_original_a10 == 0) & (x.cofog10_scope == "central government")]),
                 "expanded_strict_only": cov(x[x.cofog10_strict == 1])}, axis=1).fillna(0).astype(int)
cnt.to_csv(RES / "10_low_income_expansion/coverage_by_income.csv")
print(cnt.to_string())
SUMMARY["coverage"] = json.loads(cnt.to_json(orient="index"))
SUMMARY["new_rows"] = {"total": int((x.is_original_a10 == 0).sum()), "by_scope": x[x.is_original_a10 == 0].cofog10_scope.value_counts().to_dict(),
                       "new_economies": sorted(set(x.iso3) - set(a10.iso3)), "raw_sum_new_rows_summary": new.imf_raw_sum.describe().round(2).to_dict()}
# comparability check: where S13 and S1311 both exist (all10) in the relaxed window, how different are the shares?
both = w13.merge(w11, on=["iso3", "year"], suffixes=("_gg", "_cg")) if len(w11) else pd.DataFrame()
if len(both):
    tv = 0.5 * sum((both[f"{g}_gg"] / both.raw_sum_gg * 100 - both[f"{g}_cg"] / both.raw_sum_cg * 100).abs() for g in DIV)
    SUMMARY["central_vs_general_TVD_pp"] = {"n_country_years": int(len(both)), "mean": float(tv.mean()), "median": float(tv.median())}
# same check on high-income economies would need new downloads; instead report A10 vs. central using the sample above only.

# ------------------------------------------------------------------ (c) cold-start evaluation
INCS = ["Low income", "Lower middle income", "Upper middle income", "High income"]
T = D10


def xgb_fit_predict(Xtr, Ytr, Xte, seed, w=None):
    from xgboost import XGBRegressor
    mu, sd = Ytr.mean(0), Ytr.std(0).replace(0, 1)
    Z = (Ytr - mu) / sd
    out = {}
    for c in Ytr.columns:
        m = XGBRegressor(n_estimators=300, learning_rate=0.05, max_depth=3, subsample=0.8, colsample_bytree=0.8,
                         min_child_weight=3, reg_lambda=5.0, random_state=seed, n_jobs=1, verbosity=0)
        m.fit(Xtr, Z[c], sample_weight=w)
        out[c] = m.predict(Xte)
    return pd.DataFrame(out, index=Xte.index) * sd + mu


def run(panel, seed):
    d = panel.reset_index(drop=True)
    X = d[FEATURES].copy()
    oh = pd.get_dummies(d.income_group).reindex(columns=INCS, fill_value=0).astype(float)
    Xo = pd.concat([X, oh.add_prefix("inc_")], axis=1)
    Y = d[T]
    ctry = np.array(sorted(d.iso3.unique()))
    perm = np.random.default_rng(seed).permutation(len(ctry))
    fmap = {c: i % 6 for i, c in zip(range(len(ctry)), ctry[perm])}
    fold = d.iso3.map(fmap).values
    P = {k: np.zeros((len(d), len(T))) for k in ["peer_mean", "xgb", "xgb_weighted", "xgb_incgroup_onehot"]}
    for f in range(6):
        a, b = np.where(fold != f)[0], np.where(fold == f)[0]
        ig = d.iloc[a].groupby("income_group")[T].mean()
        P["peer_mean"][b] = np.vstack([ig.loc[g].values if g in ig.index else Y.iloc[a].mean().values for g in d.iloc[b].income_group])
        P["xgb"][b] = xgb_fit_predict(X.iloc[a], Y.iloc[a], X.iloc[b], seed).values
        cnt_g = d.iloc[a].income_group.value_counts()
        w = (1.0 / d.iloc[a].income_group.map(cnt_g)).values
        w = w / w.mean()
        P["xgb_weighted"][b] = xgb_fit_predict(X.iloc[a], Y.iloc[a], X.iloc[b], seed, w).values
        P["xgb_incgroup_onehot"][b] = xgb_fit_predict(Xo.iloc[a], Y.iloc[a], Xo.iloc[b], seed).values
    out = d[["iso3", "year", "income_group"]].copy()
    for k, v in P.items():
        out[f"tvd_{k}"] = tvd(simplex_renorm(v), Y.values)
    out["seed"] = seed
    return out


res = []
only = os.environ.get("RUNONLY")           # e.g. "expanded:0" -> compute that part only (parallel launches); parts are cached
complete = True
for regime, panel in [("A10_only", x[x.is_original_a10 == 1]), ("expanded", x)]:
    for seed in [0, 1]:
        pf = RES / f"10_low_income_expansion/part_{regime}_{seed}.csv"
        if not pf.exists():
            if only and only != f"{regime}:{seed}":
                complete = False
                continue
            t0 = time.time()
            r = run(panel, seed)
            r["regime"] = regime
            r = r.merge(x[["iso3", "year", "is_original_a10", "cofog10_scope", "cofog10_strict"]], on=["iso3", "year"], how="left")
            r.to_csv(pf, index=False)
            print(regime, seed, "done %.0fs" % (time.time() - t0), flush=True)
        res.append(pd.read_csv(pf))
if not complete:
    sys.exit(0)
R = pd.concat(res, ignore_index=True)
R.to_csv(RES / "10_low_income_expansion/rowlevel_tvd.csv", index=False)
M = ["peer_mean", "xgb", "xgb_weighted", "xgb_incgroup_onehot"]
avg = R.groupby(["regime", "iso3", "year", "income_group", "is_original_a10", "cofog10_scope", "cofog10_strict"], as_index=False)[[f"tvd_{m}" for m in M]].mean()

subsets = {"A10_rows": lambda d: d.is_original_a10 == 1,
           "new_rows_all": lambda d: d.is_original_a10 == 0,
           "new_rows_general_gov": lambda d: (d.is_original_a10 == 0) & (d.cofog10_scope == "general government"),
           "new_rows_central_gov": lambda d: (d.is_original_a10 == 0) & (d.cofog10_scope == "central government")}
tab = []
for regime in ["A10_only", "expanded"]:
    dr = avg[avg.regime == regime]
    for sname, fn in subsets.items():
        ds = dr[fn(dr)]
        if not len(ds):
            continue
        for g in INCS + ["ALL"]:
            dg = ds if g == "ALL" else ds[ds.income_group == g]
            if not len(dg):
                continue
            rr = {"train_regime": regime, "eval_subset": sname, "income_group": g, "economies": int(dg.iso3.nunique()), "country_years": len(dg)}
            for m in M:
                v = dg[f"tvd_{m}"].values
                lo, hi = boot_ci(v, dg.iso3.values)
                rr[f"TVD_{m}"], rr[f"lo_{m}"], rr[f"hi_{m}"] = float(v.mean()), lo, hi
            for m in ["xgb_weighted", "xgb_incgroup_onehot"]:
                dv = (dg[f"tvd_{m}"] - dg["tvd_xgb"]).values
                lo, hi = boot_ci(dv, dg.iso3.values)
                rr[f"delta_{m}_vs_xgb"], rr[f"dlo_{m}"], rr[f"dhi_{m}"] = float(dv.mean()), lo, hi
            tab.append(rr)
TAB = pd.DataFrame(tab)
TAB.to_csv(RES / "10_low_income_expansion/cold_by_income_expanded.csv", index=False)
print(TAB[["train_regime", "eval_subset", "income_group", "economies", "country_years"] + [f"TVD_{m}" for m in M]].round(2).to_string())
SUMMARY["cold_start"] = json.loads(TAB.to_json(orient="records"))
# data effect: same A10 test rows, A10-only vs expanded training
SUMMARY["notes"] = ("Central-government (S1311) shares are not comparable with general-government shares (local/state spending on education, health etc. is excluded); "
                    "they are flagged and should not be pooled with A10 for headline claims. 'strict' = same standard as A10.")
json.dump(SUMMARY, open(RES / "10_low_income_expansion/summary.json", "w"), indent=1, default=str)
print("saved")
