"""GovAllocXAI v2 service: peer-informed COFOG budget-composition recommendation with SHAP + LIME and a bounded allocation engine.

Trained on the OFFICIAL Eurostat/OECD COFOG panel (data/dataset_new/govalloc_cofog_panel_a16.csv). This is decision SUPPORT:
it returns a recommendation plus the evidence for it; a human analyst makes the decision.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
import shap
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor

try:
    from backend.peer_module import nearest_peers
except ImportError:  # running outside the package layout
    from peer_module import nearest_peers

ROOT = Path(__file__).resolve().parents[1]
PANELS = {"cofog16": ROOT / "data/dataset_new/govalloc_cofog_panel_a16.csv", "cofog10": ROOT / "data/dataset_new/govalloc_cofog_panel_a10.csv"}
MASTER = ROOT / "data/dataset_new/govalloc_cofog_master.csv"

SECTORS = ["general_public_services", "defence", "public_order_safety", "agriculture", "energy", "industry_construction", "transport",
           "communication_digital", "research_development", "environment", "housing_community", "water_supply", "health",
           "recreation_culture", "education", "social_protection"]
SDG_MAP = {"general_public_services": [16], "defence": [16], "public_order_safety": [16], "agriculture": [2], "energy": [7],
           "industry_construction": [8, 9], "transport": [9, 11], "communication_digital": [9], "research_development": [9],
           "environment": [13, 15], "housing_community": [11], "water_supply": [6], "health": [3], "recreation_culture": [11],
           "education": [4], "social_protection": [1, 10]}
COMPONENTS = SECTORS + ["other_residual"]
FEATURES = ["log_gdp", "log_pop", "gdp_per_capita_usd", "gdp_growth_pct", "inflation_pct", "urban_pop_pct", "pop_65plus_pct",
            "pop_0_14_pct", "tax_revenue_pct_gdp", "central_gov_debt_pct_gdp", "total_expense_pct_gdp", "unemployment_pct",
            "life_expectancy", "under5_mortality", "internet_users_pct", "electricity_access_pct", "basic_water_access_pct",
            "co2_per_capita_t", "agri_value_added_pct_gdp", "industry_value_added_pct_gdp", "trade_pct_gdp",
            "gov_effectiveness_wgi", "control_corruption_wgi", "rule_of_law_wgi", "regulatory_quality_wgi"]
SHOCKS = {  # counterfactual sensitivity presets (NOT causal estimates)
    "recession": {"gdp_growth_pct": -5.0, "unemployment_pct": +3.0, "central_gov_debt_pct_gdp": +15.0},
    "stagflation": {"gdp_growth_pct": -2.0, "inflation_pct": +8.0, "unemployment_pct": +2.0},
    "severe_stress": {"gdp_growth_pct": -15.0, "inflation_pct": +12.0, "central_gov_debt_pct_gdp": +35.0},
}


import json as _json
STACK_FILE = Path(__file__).resolve().parent / "stack_weights.json"
CLR_EPS = 0.05


def clr(Y):
    L = np.log(np.clip(np.asarray(Y, float), 0, None) + CLR_EPS)
    return L - L.mean(1, keepdims=True)


def inv_clr(Z, total=100.0):
    E = np.exp(Z - Z.max(1, keepdims=True))
    return E / E.sum(1, keepdims=True) * total


def _fit_multi(make, X, Y):
    """One regressor per column on standardised targets; returns predict(Xnew)->original units."""
    mu, sd = Y.mean(0), np.where(Y.std(0) == 0, 1, Y.std(0))
    ms = [make().fit(X, (Y[:, j] - mu[j]) / sd[j]) for j in range(Y.shape[1])]
    return lambda Xn: np.column_stack([m.predict(Xn) for m in ms]) * sd + mu


DIVISIONS = [f"GF{i:02d}" for i in range(1, 11)]
DIVISION_NAMES = {"GF01": "General public services", "GF02": "Defence", "GF03": "Public order and safety", "GF04": "Economic affairs", "GF05": "Environmental protection",
                  "GF06": "Housing and community amenities", "GF07": "Health", "GF08": "Recreation, culture and religion", "GF09": "Education", "GF10": "Social protection"}
SDG_MAP10 = {"GF01": [16], "GF02": [16], "GF03": [16], "GF04": [8, 9], "GF05": [13, 15], "GF06": [6, 11], "GF07": [3], "GF08": [11], "GF09": [4], "GF10": [1, 10]}


def _t(c: str) -> str:
    return f"cofog_{c}_pct_total"


def target_col(kind: str, c: str) -> str:
    if kind == "cofog10":
        return f"cofog10_{c}_pct_total"
    return "cofog_other_residual_pct_total" if c == "other_residual" else _t(c)


@dataclass
class V2Bundle:
    models: dict[str, XGBRegressor]
    panel: pd.DataFrame
    master: pd.DataFrame
    lo: np.ndarray
    hi: np.ndarray
    train_X: pd.DataFrame
    app_mu: np.ndarray
    app_sd: np.ndarray
    app_ref: np.ndarray
    app_loo: np.ndarray
    total_model: object = None
    stack: dict = field(default_factory=dict)
    stack_args: tuple = ()
    stack_ready: bool = False
    kind: str = "cofog16"
    components: list = field(default_factory=list)
    sdg: dict = field(default_factory=dict)
    explainers: dict[str, shap.TreeExplainer] = field(default_factory=dict)

    def explainer(self, comp: str) -> shap.TreeExplainer:
        if comp not in self.explainers:
            self.explainers[comp] = shap.TreeExplainer(self.models[comp])
        return self.explainers[comp]


def load_v2(kind: str = "cofog16") -> V2Bundle:
    panel = pd.read_csv(PANELS[kind])
    master = pd.read_csv(MASTER, usecols=["iso3", "country", "year", "income_group", *FEATURES])
    comps = COMPONENTS if kind == "cofog16" else DIVISIONS
    sdg = SDG_MAP if kind == "cofog16" else SDG_MAP10
    X = panel[FEATURES]
    models = {}
    for c in comps:
        models[c] = XGBRegressor(n_estimators=300, learning_rate=0.05, max_depth=3, subsample=0.8, colsample_bytree=0.8,
                                 min_child_weight=3, reg_lambda=5.0, random_state=42, n_jobs=-1, verbosity=0).fit(X, panel[target_col(kind, c)])
    Y = panel[[target_col(kind, c) for c in comps]]
    Xf = X.fillna(X.median())
    mu, sd = Xf.mean().values, Xf.std().replace(0, 1).values
    ref = ((Xf - mu) / sd).groupby(panel.iso3.values).median().values          # one standardised vector per training economy
    dd = np.sqrt(((ref[:, None, :] - ref[None, :, :]) ** 2).sum(2)); np.fill_diagonal(dd, np.inf)
    loo = np.sort(dd, 1)[:, :5].mean(1)                                          # each training economy vs. its 5 nearest others
    # total-budget module: general-government total expenditure as % of GDP (observed Eurostat rows only), ridge on the same features
    tot = pd.read_csv(PANELS["cofog16"]); tot = tot[tot["cofog_total_expenditure_pct_gdp"].notna()]
    total_model = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=10.0)).fit(tot[FEATURES], tot["cofog_total_expenditure_pct_gdp"])
    # the stack members are fitted lazily on the first request for this panel (keeps start-up fast)
    return V2Bundle(models, panel, master, Y.min().values * 0.5, Y.max().values * 1.5, X, mu, sd, ref, loo, total_model, {}, (kind, panel, X, Y), False, kind, list(comps), sdg)


def _load_stack(kind, panel, X, Y):
    """Cold-start Stack v2.1: members peer_mean, ridge, xgb_clr, cat_clr blended with NNLS weights exported by pipeline/18_export_stack_weights.py."""
    if not STACK_FILE.exists():
        return {}
    cfg = _json.load(open(STACK_FILE)).get(kind)
    if not cfg:
        return {}
    from catboost import CatBoostRegressor
    Xn, Yn = X.values.astype(float), Y.values.astype(float)
    med = np.nanmedian(Xn, 0)
    ridge_pipe = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=10.0))
    ridge_pred = _fit_multi(lambda: make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=10.0)), Xn, Yn)
    Z = clr(Yn)
    xgb_pred = _fit_multi(lambda: XGBRegressor(n_estimators=300, learning_rate=0.05, max_depth=3, subsample=0.8, colsample_bytree=0.8, min_child_weight=3,
                                               reg_lambda=5.0, random_state=42, n_jobs=-1, verbosity=0), Xn, Z)
    cat_pred = _fit_multi(lambda: CatBoostRegressor(iterations=300, learning_rate=0.07, depth=4, l2_leaf_reg=5.0, random_seed=42, verbose=0, thread_count=4), Xn, Z)
    group_mean = panel.assign(**{f"_y{j}": Yn[:, j] for j in range(Yn.shape[1])}).groupby("income_group")[[f"_y{j}" for j in range(Yn.shape[1])]].mean()
    return {"W": np.array(cfg["weights"]), "ridge": ridge_pred, "xgb": xgb_pred, "cat": cat_pred, "group_mean": group_mean, "global_mean": Yn.mean(0), "med": med, "conformal": cfg.get("conformal")}


def stack_predict(b, x_row: pd.DataFrame, income_group: str | None):
    if not b.stack_ready:
        b.stack = _load_stack(*b.stack_args)
        b.stack_ready = True
    st = b.stack
    if not st:
        return None
    xv = x_row.values.astype(float)
    peer = st["group_mean"].loc[income_group].values if income_group in st["group_mean"].index else st["global_mean"]
    preds = [peer[None, :], st["ridge"](xv), inv_clr(st["xgb"](xv)), inv_clr(st["cat"](xv))]
    blend = sum(p * st["W"][i][None, :] for i, p in enumerate(preds))
    return blend[0]


def bounded_projection(p: np.ndarray, lo: np.ndarray, hi: np.ndarray, total: float = 100.0) -> np.ndarray:
    a, b = (lo - p).min() - total, (hi - p).max() + total
    for _ in range(100):
        mid = (a + b) / 2
        if np.clip(p + mid, lo, hi).sum() > total:
            b = mid
        else:
            a = mid
    return np.clip(p + (a + b) / 2, lo, hi)


def recommend(b: V2Bundle, iso3: str, year: int | None, overrides: dict[str, float], shock: str | None, lime_sector: str | None,
              top_k: int = 5, total_budget_usd: float | None = None) -> dict:
    rows = b.master[b.master.iso3 == iso3.upper()]
    if rows.empty:
        raise KeyError(f"Unknown economy '{iso3}'.")
    row = rows[rows.year == year].iloc[0] if year is not None and (rows.year == year).any() else rows.sort_values("year").iloc[-1]
    feats = row[FEATURES].astype(float).copy()
    for k, v in overrides.items():
        if k not in FEATURES:
            raise ValueError(f"Unknown feature '{k}'.")
        feats[k] = float(v)
    if shock:
        for k, dv in SHOCKS[shock].items():
            feats[k] = feats[k] + dv
        if "gdp_growth_pct" in SHOCKS[shock]:
            pass
    x = pd.DataFrame([feats.values], columns=FEATURES)
    xgb_raw = np.array([float(b.models[c].predict(x)[0]) for c in b.components])
    stacked = stack_predict(b, x, str(row.get("income_group")) if "income_group" in row else None)
    raw = stacked if stacked is not None else xgb_raw
    raw = np.clip(raw, 0, None)
    raw = raw / raw.sum() * 100
    alloc = bounded_projection(raw, b.lo, b.hi)
    last = b.panel[b.panel.iso3 == iso3.upper()].sort_values("year")
    last_obs = None
    if not last.empty:
        lr = last.iloc[-1]
        last_obs = {"year": int(lr.year), **{c: float(lr[target_col(b.kind, c)]) for c in b.components}}
    comps = []
    for j, c in enumerate(b.components):
        sv = b.explainer(c).shap_values(x)[0]
        order = np.argsort(-np.abs(sv))[:top_k]
        comps.append({"component": c, "sdg": b.sdg.get(c, []), "label": DIVISION_NAMES.get(c, c), "recommended_share_pct": float(alloc[j]), "raw_model_share_pct": float(raw[j]), "xgboost_member_share_pct": float(xgb_raw[j]),
                      "last_observed_share_pct": None if last_obs is None else last_obs[c],
                      "top_shap": [{"feature": FEATURES[i], "feature_value": float(x.iloc[0, i]), "shap_pp": float(sv[i])} for i in order]})
    # applicability: how far is this economy's feature vector from its 5 nearest TRAINING economies (standardised), vs. the training economies themselves
    xf = np.where(np.isnan(x.values[0]), b.train_X.median().values, x.values[0])
    zz = ((xf - b.app_mu) / b.app_sd)[None, :] - b.app_ref
    dist = np.sqrt((zz ** 2).sum(1))
    nov = float(np.sort(dist)[:5].mean())
    pct = float((b.app_loo < nov).mean() * 100)
    applicability = {"novelty_score": nov, "percentile_among_training_economies": pct,
                     "status": "typical" if pct < 75 else ("unusual - treat with caution" if pct < 95 else "outside typical training range - recommendation is an extrapolation")}
    gdp_usd = float(10 ** x.iloc[0]["log_gdp"])
    pred_total_pct_gdp = float(b.total_model.predict(x)[0])
    total_info = {"predicted_total_expenditure_pct_gdp": pred_total_pct_gdp, "gdp_usd": gdp_usd, "implied_total_usd": pred_total_pct_gdp / 100 * gdp_usd,
                  "used_total_usd": float(total_budget_usd) if total_budget_usd else pred_total_pct_gdp / 100 * gdp_usd,
                  "source": "user-supplied" if total_budget_usd else "model estimate (ridge trained on general-government totals of 30 OECD/EU economies (716 country-years); leave-country-out MAE 3.8 pp of GDP, against 5.6 pp for the group mean; the 1.8 pp figure in the paper is for a delta model with history that this API does not serve) - treat as indicative"}
    for c_ in comps:
        c_["amount_usd"] = c_["recommended_share_pct"] / 100 * total_info["used_total_usd"]
    # intervals (conformal-style, from out-of-fold residuals of the stack) and similar-economy explanation
    conf = b.stack.get("conformal") if stacked is not None and b.stack else None
    grp = str(row.get("income_group")) if "income_group" in row else None
    if conf:
        basis = "income-group" if grp in conf["groups"] else "global"
        qsrc = conf["groups"][grp] if grp in conf["groups"] else conf["global"]
        for j, c_ in enumerate(comps):
            for lvl, key in (("0.8", "interval_80_pp"), ("0.9", "interval_90_pp")):
                q = qsrc[lvl][j]
                c_[key] = [max(0.0, c_["recommended_share_pct"] - q), min(100.0, c_["recommended_share_pct"] + q)]
        interval_info = {"basis": basis, "note": conf["note"], "group_calibration_rows": conf["group_rows"].get(grp)}
    else:
        interval_info = None
    tcols = [target_col(b.kind, c) for c in b.components]
    try:
        peers_res = nearest_peers(b.panel[b.panel.iso3 != iso3.upper()], feats, k=5, targets=tcols, features=FEATURES)
        names = b.master.drop_duplicates("iso3").set_index("iso3")["country"].to_dict()
        similar = [{"iso3": p_["iso3"], "country": names.get(p_["iso3"], p_["iso3"]), "years": p_["years"], "distance": p_["distance"], "weight": p_["weight"],
                    "shares_pct": {c: p_["shares"][target_col(b.kind, c)] for c in b.components}} for p_ in peers_res["peers"]]
    except Exception:  # noqa: BLE001
        similar = []
    out = {"intervals": interval_info, "similar_economies": similar, "total_budget": total_info, "applicability": applicability, "iso3": iso3.upper(), "country": str(row["country"]), "feature_year": int(row["year"]), "shock": shock, "overrides": overrides,
           "panel": b.kind, "training_rows": int(len(b.panel)), "training_economies": int(b.panel.iso3.nunique()), "sum_check": float(alloc.sum()), "components": comps,
           "model": "Stack v2.1 (peer mean + ridge + XGBoost-CLR + CatBoost-CLR, NNLS weights); SHAP/LIME explain the XGBoost member" if stacked is not None else "XGBoost", "note": "Decision-support recommendation learned from peer economies' official COFOG allocations; not a causal estimate and not a decision."}
    if lime_sector:
        if lime_sector not in b.components:
            raise ValueError(f"Unknown sector '{lime_sector}'.")
        from lime.lime_tabular import LimeTabularExplainer
        Xtr = b.train_X.values
        med = np.nanmedian(Xtr, 0)
        Xf = np.where(np.isnan(Xtr), med, Xtr)
        ex = LimeTabularExplainer(Xf, feature_names=FEATURES, mode="regression", discretize_continuous=False, random_state=0)
        mdl = b.models[lime_sector]
        e = ex.explain_instance(np.where(np.isnan(x.values[0]), med, x.values[0]), lambda a: mdl.predict(pd.DataFrame(a, columns=FEATURES)),
                                num_features=len(FEATURES), num_samples=1500)
        sd = Xf.std(0)
        sd[sd == 0] = 1
        mu = Xf.mean(0)
        w = dict(e.local_exp[list(e.local_exp)[0]])
        out["lime"] = {"sector": lime_sector, "local_r2": float(e.score),
                       "features": sorted([{"feature": FEATURES[j], "weight_per_sd": float(v), "contribution_pp": float(v * (x.values[0][j] - mu[j]) / sd[j])}
                                           for j, v in w.items()], key=lambda r: -abs(r["contribution_pp"]))[:10]}
    return out
