"""Model-selection step (VALIDATION ONLY, no test data): does a richer feature spec help?
Spec BASE   = FEATURES
Spec PLUS   = FEATURES + region/income-group one-hot + year-on-year changes of key macro-fiscal features
Selection window: train <= 2016, validate 2017-2019 (the 2020-2024 test window is never touched here).
Outputs results/02_main_experiments/feature_spec_selection.csv
"""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from gov_common import *

d = load_cofog(); T = TARGETS_A; LAG = [f"lag_{t}" for t in T]
DELTA_BASE = ["log_gdp", "gdp_growth_pct", "inflation_pct", "unemployment_pct", "central_gov_debt_pct_gdp", "tax_revenue_pct_gdp", "total_expense_pct_gdp"]
d = d.sort_values(["iso3", "year"]).reset_index(drop=True)
for f in DELTA_BASE:
    d[f"d_{f}"] = d.groupby("iso3")[f].diff()
DCOLS = [f"d_{f}" for f in DELTA_BASE]
oh = pd.get_dummies(d[["region", "income_group"]], dtype=float); OH = list(oh.columns)
d = pd.concat([d, oh], axis=1)
specs = {"BASE": FEATURES, "PLUS_groups": FEATURES + OH, "PLUS_changes": FEATURES + DCOLS, "PLUS_both": FEATURES + OH + DCOLS}
tr = d[(d.year <= 2016) & d.has_lag]; va = d[(d.year >= 2017) & (d.year <= 2019) & d.has_lag]
rows = []
for name, cols in specs.items():
    D = fit_predict_multi("xgb", tr[cols + LAG], pd.DataFrame(tr[T].values - tr[LAG].values, columns=T, index=tr.index), va[cols + LAG])
    P = simplex_renorm(va[LAG].values + D.values)
    rows.append({"regime": "history (delta learner)", "spec": name, "n_features": len(cols), "TVD_val": float(tvd(P, va[T].values).mean())})
rows.append({"regime": "history (delta learner)", "spec": "persistence", "n_features": 0, "TVD_val": float(tvd(va[LAG].values, va[T].values).mean())})
tr2 = d[d.year <= 2016]; va2 = d[(d.year >= 2017) & (d.year <= 2019)]
for name, cols in specs.items():
    P = fit_predict_multi("xgb", tr2[cols], tr2[T], va2[cols])
    rows.append({"regime": "cold-start features-only", "spec": name, "n_features": len(cols), "TVD_val": float(tvd(simplex_renorm(P.values), va2[T].values).mean())})
R = pd.DataFrame(rows); R.to_csv(RES / "02_main_experiments/feature_spec_selection.csv", index=False); print(R.round(3).to_string())
