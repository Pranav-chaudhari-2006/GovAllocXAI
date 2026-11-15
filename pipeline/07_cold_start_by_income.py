"""Cold-start error BY INCOME GROUP and applicability (novelty) score on the wide panel A10 (85 economies, Eurostat+OECD+IMF).
Question answered: is a model trained on all economies reliable for lower-income economies it has seen few of?
Method: leave-country-out (6 folds, seed 0); methods: income-group peer mean vs XGBoost (raw) vs ridge.
Applicability score = distance of an economy's standardised features to its k=5 nearest TRAINING economies (country medians), reported per group;
we also correlate it with the model's TVD (does 'unlike the training data' predict larger errors?).
Outputs: results/06_cold_start_by_income/cold_by_income.csv, results/06_cold_start_by_income/applicability.json
"""
import json
import sys

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from gov_common import *  # noqa: F401,F403

d = pd.read_csv(PROC / "govallocxai_new_cofog10_panel.csv").sort_values(["iso3", "year"]).reset_index(drop=True)
T = [f"cofog10_GF{i:02d}_pct_total" for i in range(1, 11)]
X, Y = d[FEATURES], d[T]
ctry = d.iso3.unique(); perm = np.random.default_rng(0).permutation(len(ctry))
fold = d.iso3.map({c: i % 6 for i, c in zip(range(len(ctry)), ctry[perm])}).values
oof = {k: np.zeros((len(d), len(T))) for k in ["peer_mean", "ridge", "xgb"]}
novelty = np.zeros(len(d))
Xs = X.fillna(X.median())
for f in range(6):
    a, b = np.where(fold != f)[0], np.where(fold == f)[0]
    ig = d.iloc[a].groupby("income_group")[T].mean()
    oof["peer_mean"][b] = np.vstack([ig.loc[g].values if g in ig.index else Y.iloc[a].mean().values for g in d.iloc[b].income_group])
    oof["ridge"][b] = fit_predict_multi("ridge", X.iloc[a], Y.iloc[a], X.iloc[b]).values
    oof["xgb"][b] = fit_predict_multi("xgb", X.iloc[a], Y.iloc[a], X.iloc[b]).values
    # applicability: distance to the 5 nearest training economies in standardised feature space
    mu, sd = Xs.iloc[a].mean(), Xs.iloc[a].std().replace(0, 1)
    A = ((Xs.iloc[a] - mu) / sd).groupby(d.iso3.iloc[a].values).median().values
    B = ((Xs.iloc[b] - mu) / sd).values
    dist = np.sqrt(((B[:, None, :] - A[None, :, :]) ** 2).sum(2))
    novelty[b] = np.sort(dist, 1)[:, :5].mean(1)
rows = []
for g, idx in d.groupby("income_group").groups.items():
    idx = np.array(list(idx))
    r = {"income_group": g, "economies": int(d.iso3.iloc[idx].nunique()), "country_years": len(idx), "mean_novelty": float(novelty[idx].mean())}
    for k in oof:
        t = tvd(simplex_renorm(oof[k][idx]), Y.values[idx])
        r[f"TVD_{k}"] = float(t.mean())
    rows.append(r)
R = pd.DataFrame(rows).sort_values("mean_novelty"); R.to_csv(RES / "06_cold_start_by_income/cold_by_income.csv", index=False); print(R.round(3).to_string())
t_xgb = tvd(simplex_renorm(oof["xgb"]), Y.values)
rho = spearmanr(novelty, t_xgb)
json.dump({"spearman_novelty_vs_TVD_xgb": float(rho[0]), "p": float(rho[1]), "n": len(d), "economies": int(d.iso3.nunique())}, open(RES / "06_cold_start_by_income/applicability.json", "w"), indent=1)
print("novelty vs error: rho=%.3f p=%.2g" % rho)
