"""Total-budget module: general-government total expenditure as % of GDP (observed, Eurostat COFOG panel). With it, shares -> amounts:
amount_k = share_k/100 * total_%GDP/100 * GDP_usd.
Evaluation: (a) temporal one-step-ahead (train<=2019 -> test 2020-24): persistence vs Delta-XGB vs Delta-ridge; (b) cold start leave-country-out.
Outputs results/07_total_budget/total_budget.csv and 07_total_budget/summary.json
"""
import json
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from gov_common import *  # noqa: F401,F403

d = pd.read_csv(PROC / "govalloc_cofog_panel_a16.csv").sort_values(["iso3", "year"]).reset_index(drop=True)
y = "cofog_total_expenditure_pct_gdp"
d = d[d[y].notna()].reset_index(drop=True)
d["lag"] = d.groupby("iso3")[y].shift(1)
ok = (d.year - d.groupby("iso3")["year"].shift(1)) == 1
d.loc[~ok, "lag"] = np.nan
rows = []


def add(proto, method, yt, p, groups):
    e = np.abs(np.asarray(p) - np.asarray(yt))
    lo, hi = boot_ci(e, groups)
    rows.append({"protocol": proto, "method": method, "n": len(yt), "MAE_pp_gdp": float(e.mean()), "lo": lo, "hi": hi,
                 "RMSE": float(np.sqrt((e ** 2).mean()))})


tr, te = d[(d.year <= 2019) & d.lag.notna()], d[(d.year >= 2020) & d.lag.notna()]
add("temporal 2020-24", "persistence", te[y], te.lag, te.iso3.values)
add("temporal 2020-24", "country mean", te[y], te.iso3.map(d[d.year <= 2019].groupby("iso3")[y].mean()).fillna(tr[y].mean()), te.iso3.values)
for m in ["ridge", "xgb", "cat"]:
    D = fit_predict_multi(m, tr[FEATURES + ["lag"]], (tr[y] - tr.lag).to_frame(y), te[FEATURES + ["lag"]]).values[:, 0]
    add("temporal 2020-24", f"delta {m}", te[y], te.lag + D, te.iso3.values)
# cold start
ctry = d.iso3.unique(); perm = np.random.default_rng(0).permutation(len(ctry))
fold = d.iso3.map({c: i % 6 for i, c in zip(range(len(ctry)), ctry[perm])}).values
oof = {k: np.zeros(len(d)) for k in ["global mean", "income-group mean", "ridge", "xgb", "cat"]}
for f in range(6):
    a, b = np.where(fold != f)[0], np.where(fold == f)[0]
    oof["global mean"][b] = d.iloc[a][y].mean()
    ig = d.iloc[a].groupby("income_group")[y].mean(); oof["income-group mean"][b] = d.iloc[b].income_group.map(ig).fillna(d.iloc[a][y].mean()).values
    for m in ["ridge", "xgb", "cat"]:
        oof[m][b] = fit_predict_multi(m, d.iloc[a][FEATURES], d.iloc[a][[y]], d.iloc[b][FEATURES]).values[:, 0]
for k, p in oof.items():
    add("cold start leave-country-out", k, d[y], p, d.iso3.values)
R = pd.DataFrame(rows); R.to_csv(RES / "07_total_budget/total_budget.csv", index=False); print(R.round(3).to_string())
json.dump({"n_rows": len(d), "n_economies": int(d.iso3.nunique()), "target_mean_pct_gdp": float(d[y].mean()), "target_sd": float(d[y].std())}, open(RES / "07_total_budget/summary.json", "w"), indent=1)
