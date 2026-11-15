"""Institutional-features ablation (limited to what is reachable keylessly): WGI Voice & Accountability and Political Stability (World Bank API, source 3),
plus their 2-year changes. Election-year, fiscal-rule and IMF-programme datasets were NOT obtainable without login/manual download (documented in docs/12).
Ablation on A10: baseline FEATURES vs FEATURES + inst_*; cold-start leave-country-out (6 folds, seeds 0,1) and annual Delta-xgb (train<=2019, test 2020-24; also 2020-21 only).
Outputs data/dataset_new/govallocxai_new_institutional_features.csv, results/18_institutional_features/wgi_*.csv|json
"""
import importlib.util
import json
import os
import pathlib
import sys
import time

os.environ.setdefault("OMP_NUM_THREADS", "4")
import numpy as np
import pandas as pd
import requests

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
from gov_common import *  # noqa: F401,F403

spec = importlib.util.spec_from_file_location("arch21", HERE / "06_stack_architecture.py")
arch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(arch)

frames = []
for code, name in [("VA", "inst_voice_accountability"), ("PV", "inst_political_stability")]:
    rows = None
    for _ in range(4):
        try:
            j = requests.get(f"https://api.worldbank.org/v2/country/all/indicator/GOV_WGI_{code}.EST", params={"source": 3, "format": "json", "per_page": 20000, "date": "2000:2024"}, timeout=90).json()
            rows = [(r["countryiso3code"], int(r["date"]), r["value"]) for r in j[1] if r["value"] is not None and r["countryiso3code"]]
            break
        except Exception:  # noqa: BLE001
            time.sleep(3)
    if rows is None:
        raise SystemExit(f"could not download WGI {code}")
    frames.append(pd.DataFrame(rows, columns=["iso3", "year", name]).drop_duplicates(["iso3", "year"]))
inst = frames[0].merge(frames[1], on=["iso3", "year"], how="outer").sort_values(["iso3", "year"])
for c in ["inst_voice_accountability", "inst_political_stability"]:
    inst[c + "_chg2"] = inst.groupby("iso3")[c].diff(2)
inst.to_csv(PROC / "govallocxai_new_institutional_features.csv", index=False)
INST = [c for c in inst.columns if c.startswith("inst_")]

out = {}
d, T = arch.load_panel("A10")
d = d.reset_index(drop=True).merge(inst, on=["iso3", "year"], how="left")
cov = {c: float(d[c].notna().mean()) for c in INST}
out["coverage_A10"] = cov
print("coverage", cov, flush=True)

# cold start
Y = d[T]
rows = []
for seed in [0, 1]:
    ctry = d.iso3.unique(); perm = np.random.default_rng(seed).permutation(len(ctry))
    fold = d.iso3.map({c: i % 6 for i, c in zip(range(len(ctry)), ctry[perm])}).values
    for name, cols in [("base", FEATURES), ("base+inst", FEATURES + INST)]:
        oof = np.zeros((len(d), len(T)))
        for f in range(6):
            a, b = np.where(fold != f)[0], np.where(fold == f)[0]
            oof[b] = arch.fit_predict_multi("xgb", d.iloc[a][cols], Y.iloc[a], d.iloc[b][cols], 42 + seed).values
        t = tvd(simplex_renorm(oof), Y.values)
        rows.append({"regime": "cold-start", "seed": seed, "features": name, "tvd": t, "iso3": d.iso3.values, "year": d.year.values})
cs = {}
for seed in [0, 1]:
    a = [r for r in rows if r["seed"] == seed and r["features"] == "base"][0]; b = [r for r in rows if r["seed"] == seed and r["features"] == "base+inst"][0]
    gain = a["tvd"] - b["tvd"]; lo, hi = boot_ci(gain, d.iso3.values)
    cs[f"seed{seed}"] = {"TVD_base": float(a["tvd"].mean()), "TVD_inst": float(b["tvd"].mean()), "gain": float(gain.mean()), "ci95": [lo, hi]}
out["cold_start"] = cs
print(cs, flush=True)

# annual
ok = d.has_lag
tr, te = d[ok & (d.year <= 2019)], d[ok & (d.year >= 2020)]
L1, L1te = tr[[f"h1_{t}" for t in T]].values, te[[f"h1_{t}" for t in T]].values
an = {}
tv = {}
for name, cols in [("base", FEATURES), ("base+inst", FEATURES + INST)]:
    X1 = cols + [f"h1_{t}" for t in T]
    D = arch.fit_predict_multi("xgb", tr[X1], pd.DataFrame(tr[T].values - L1, columns=T, index=tr.index), te[X1]).values
    tv[name] = tvd(simplex_renorm(L1te + D), te[T].values)
for lab, m in [("2020-24", np.ones(len(te), bool)), ("2020-21", (te.year <= 2021).values)]:
    gain = (tv["base"] - tv["base+inst"])[m]
    lo, hi = boot_ci(gain, te.iso3.values[m])
    an[lab] = {"n": int(m.sum()), "TVD_base": float(tv["base"][m].mean()), "TVD_inst": float(tv["base+inst"][m].mean()), "gain": float(gain.mean()), "ci95": [lo, hi]}
out["annual"] = an
print(an, flush=True)
json.dump(out, open(RES / "18_institutional_features/wgi_summary.json", "w"), indent=1, default=float)
pd.DataFrame([{"regime": "cold-start", **{k: v for k, v in c.items()}, "seed": s} for s, c in cs.items()]).to_csv(RES / "18_institutional_features/wgi_cold.csv", index=False)
pd.DataFrame([{"window": k, **v} for k, v in an.items()]).to_csv(RES / "18_institutional_features/wgi_annual.csv", index=False)
print("done")
