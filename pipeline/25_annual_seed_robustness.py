"""Experiment U: learner-seed robustness of the headline annual Delta-hybrid gain over persistence (panel A16).

Re-fits the 50% XGB + 50% CatBoost Delta-learner of 04_experiments_main.py with five learner seeds (42-46) on the same
temporal split (train <=2019, test 2020-24) and reports the paired TVD gain over persistence with a cluster bootstrap.
Output: results/19_annual_seed_robustness/annual_seeds.csv, results/19_annual_seed_robustness/summary.json
"""
import json, sys
import numpy as np, pandas as pd
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from gov_common import *

d = load_cofog(); T = TARGETS_A; LAG = [f"lag_{t}" for t in T]
tr = d[(d.year <= 2019) & d.has_lag]; te = d[(d.year >= 2020) & d.has_lag]
Ytr, Yte = tr[T], te[T]
Xtr_l, Xte_l = tr[FEATURES + LAG], te[FEATURES + LAG]
Dtr = pd.DataFrame(Ytr.values - tr[LAG].values, columns=T, index=tr.index)
t_pers = tvd(simplex_renorm(te[LAG].values), Yte.values)
rows = []
for seed in [42, 43, 44, 45, 46]:
    Dx = fit_predict_multi("xgb", Xtr_l, Dtr, Xte_l, seed=seed); Dc = fit_predict_multi("cat", Xtr_l, Dtr, Xte_l, seed=seed)
    for name, D in [("hybrid", 0.5 * Dx + 0.5 * Dc), ("xgb", Dx), ("cat", Dc)]:
        t = tvd(simplex_renorm(te[LAG].values + D.values), Yte.values)
        diff = t_pers - t; lo, hi = boot_ci(diff, te.iso3.values)
        rows.append({"model": name, "seed": seed, "TVD": float(t.mean()), "gain_vs_persistence": float(diff.mean()), "ci95_lo": lo, "ci95_hi": hi, "share_rows_improved": float((diff > 0).mean())})
R = pd.DataFrame(rows); R.to_csv(RES / "19_annual_seed_robustness/annual_seeds.csv", index=False)
summ = {"persistence_TVD": float(t_pers.mean())}
for name, g in R.groupby("model"):
    summ[name] = {"mean_gain": float(g.gain_vs_persistence.mean()), "min_gain": float(g.gain_vs_persistence.min()), "max_gain": float(g.gain_vs_persistence.max()),
                  "n_seeds_ci_excludes_zero": int((g.ci95_lo > 0).sum()), "n_seeds": int(len(g))}
json.dump(summ, open(RES / "19_annual_seed_robustness/summary.json", "w"), indent=1)
print(R.round(4).to_string()); print(json.dumps(summ, indent=1))
