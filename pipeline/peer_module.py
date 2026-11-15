"""Explainable 'similar countries' (KNN peer) predictor. Pure pandas/numpy; importable by the backend.

    from peer_module import nearest_peers, knn_peer_predict
    res = nearest_peers(train_df, query_row, k=5, targets=T)

Method: features are median-filled and standardised using TRAINING economies only; each training economy is
represented by the median of its feature vector over years; the query (a specific country-year row, or a median
vector) is compared with every training economy by Euclidean distance; the k nearest economies are averaged with
inverse-distance weights to give the predicted composition (shares, sums to ~100).
"""
from __future__ import annotations
import numpy as np
import pandas as pd

DEFAULT_FEATURES = ["log_gdp", "log_pop", "gdp_per_capita_usd", "gdp_growth_pct", "inflation_pct", "urban_pop_pct",
                    "pop_65plus_pct", "pop_0_14_pct", "tax_revenue_pct_gdp", "central_gov_debt_pct_gdp",
                    "total_expense_pct_gdp", "unemployment_pct", "life_expectancy", "under5_mortality",
                    "internet_users_pct", "electricity_access_pct", "basic_water_access_pct", "co2_per_capita_t",
                    "agri_value_added_pct_gdp", "industry_value_added_pct_gdp", "trade_pct_gdp",
                    "gov_effectiveness_wgi", "control_corruption_wgi", "rule_of_law_wgi", "regulatory_quality_wgi"]


def _fit_space(train_df, features, id_col="iso3"):
    med = train_df[features].median()
    Xf = train_df[features].fillna(med)
    mu, sd = Xf.mean(), Xf.std().replace(0, 1).fillna(1)
    Z = (Xf - mu) / sd
    eco = Z.groupby(train_df[id_col].values).median()            # economy-level feature vector (median over years)
    return med, mu, sd, eco


def _project(df, features, med, mu, sd):
    return ((df[features].fillna(med) - mu) / sd).values


def knn_peer_predict(train_df, test_df, targets, k=5, features=None, id_col="iso3", power=1.0, eps=1e-6, return_idx=False):
    """Vectorised prediction for every row of test_df. Returns (n_test, K) array of predicted shares."""
    features = features or DEFAULT_FEATURES
    med, mu, sd, eco = _fit_space(train_df, features, id_col)
    share = train_df[targets].groupby(train_df[id_col].values).mean().reindex(eco.index)   # economy mean composition
    B = _project(test_df, features, med, mu, sd)
    D = np.sqrt(((B[:, None, :] - eco.values[None, :, :]) ** 2).sum(2))
    k = min(k, D.shape[1])
    idx = np.argsort(D, 1)[:, :k]
    dk = np.take_along_axis(D, idx, 1)
    w = 1.0 / (dk + eps) ** power
    w /= w.sum(1, keepdims=True)
    S = share.values[idx]                                          # (n, k, K)
    P = (S * w[:, :, None]).sum(1)
    return (P, idx, w) if return_idx else P


def nearest_peers(train_df, query_row, k=5, targets=None, features=None, id_col="iso3", year_col="year", power=1.0):
    """Explain one query. query_row: pd.Series or dict with the feature columns (a country-year).

    Returns dict: peers (list of dicts: iso3, years 'min-max', n_years, distance, weight, shares {target: pp}),
    prediction {target: pp}, and the feature-space meta (median/mean/std not returned; recomputed on demand).
    """
    features = features or DEFAULT_FEATURES
    q = pd.DataFrame([dict(query_row)] if not isinstance(query_row, pd.Series) else [query_row.to_dict()])
    if targets is None:
        targets = [c for c in train_df.columns if c.endswith("_pct_total") and not c.startswith(("lag_", "h1_", "h2_", "hT_", "hM_"))]
    P, idx, w = knn_peer_predict(train_df, q, targets, k, features, id_col, power, return_idx=True)
    _, _, _, eco = _fit_space(train_df, features, id_col)
    med, mu, sd, _ = _fit_space(train_df, features, id_col)
    qz = _project(q, features, med, mu, sd)[0]
    peers = []
    for j, wj in zip(idx[0], w[0]):
        iso = eco.index[j]
        sub = train_df[train_df[id_col] == iso]
        peers.append({"iso3": iso, "years": f"{int(sub[year_col].min())}-{int(sub[year_col].max())}" if year_col in sub else None,
                      "n_years": int(len(sub)), "distance": float(np.sqrt(((qz - eco.values[j]) ** 2).sum())),
                      "weight": float(wj), "shares": {t: float(sub[t].mean()) for t in targets}})
    return {"peers": peers, "prediction": dict(zip(targets, map(float, P[0]))), "k": len(peers)}
