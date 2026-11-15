"""Shared utilities for GovAllocXAI v2 experiments: features, models, metrics, constrained allocation engine."""
from __future__ import annotations
import pathlib, warnings
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parents[1]
PROC = ROOT / "data/dataset_new"
OLD = ROOT / "data/dataset_old"
RES = ROOT / "results"
RES.mkdir(exist_ok=True)

SECTORS = ["general_public_services", "defence", "public_order_safety", "agriculture", "energy",
           "industry_construction", "transport", "communication_digital", "research_development",
           "environment", "housing_community", "water_supply", "health", "recreation_culture",
           "education", "social_protection"]
SECTOR_LABEL = {s: s.replace("_", " ").title().replace("And", "&") for s in SECTORS}
SECTOR_LABEL.update({"research_development": "R&D (economic)", "communication_digital": "Communication/Digital",
                     "industry_construction": "Industry & Construction", "housing_community": "Housing & Community",
                     "public_order_safety": "Public Order & Safety", "general_public_services": "General Public Services"})
# COFOG division -> primary SDG(s) (crosswalk used by the reporting layer; NOT a model input)
SDG_MAP = {"general_public_services": [16], "defence": [16], "public_order_safety": [16], "agriculture": [2],
           "energy": [7], "industry_construction": [8, 9], "transport": [9, 11], "communication_digital": [9],
           "research_development": [9], "environment": [13, 15], "housing_community": [11], "water_supply": [6],
           "health": [3], "recreation_culture": [11], "education": [4], "social_protection": [1, 10]}
TARGETS_A = [f"cofog_{s}_pct_total" for s in SECTORS] + ["cofog_other_residual_pct_total"]

FEATURES = ["log_gdp", "log_pop", "gdp_per_capita_usd", "gdp_growth_pct", "inflation_pct", "urban_pop_pct", "pop_65plus_pct",
            "pop_0_14_pct", "tax_revenue_pct_gdp", "central_gov_debt_pct_gdp", "total_expense_pct_gdp", "unemployment_pct",
            "life_expectancy", "under5_mortality", "internet_users_pct", "electricity_access_pct", "basic_water_access_pct",
            "co2_per_capita_t", "agri_value_added_pct_gdp", "industry_value_added_pct_gdp", "trade_pct_gdp",
            "gov_effectiveness_wgi", "control_corruption_wgi", "rule_of_law_wgi", "regulatory_quality_wgi"]
FEATURE_LABEL = {"log_gdp": "log10 GDP", "log_pop": "log10 population", "gdp_per_capita_usd": "GDP per capita",
                 "gdp_growth_pct": "GDP growth", "inflation_pct": "Inflation", "urban_pop_pct": "Urban pop. %",
                 "pop_65plus_pct": "Pop. 65+ %", "pop_0_14_pct": "Pop. 0-14 %", "tax_revenue_pct_gdp": "Tax revenue %GDP",
                 "central_gov_debt_pct_gdp": "Central gov. debt %GDP", "total_expense_pct_gdp": "Gov. expense %GDP",
                 "unemployment_pct": "Unemployment", "life_expectancy": "Life expectancy", "under5_mortality": "Under-5 mortality",
                 "internet_users_pct": "Internet users %", "electricity_access_pct": "Electricity access",
                 "basic_water_access_pct": "Basic water access", "co2_per_capita_t": "CO2 per capita",
                 "agri_value_added_pct_gdp": "Agriculture VA %GDP", "industry_value_added_pct_gdp": "Industry VA %GDP",
                 "trade_pct_gdp": "Trade %GDP", "gov_effectiveness_wgi": "Gov. effectiveness (WGI)",
                 "control_corruption_wgi": "Control of corruption (WGI)", "rule_of_law_wgi": "Rule of law (WGI)",
                 "regulatory_quality_wgi": "Regulatory quality (WGI)"}


def load_cofog() -> pd.DataFrame:
    d = pd.read_csv(PROC / "govallocxai_new_cofog_panel.csv")
    d = d.sort_values(["iso3", "year"]).reset_index(drop=True)
    for t in TARGETS_A:
        d[f"lag_{t}"] = d.groupby("iso3")[t].shift(1)
        yr = d.groupby("iso3")["year"].shift(1)
        d.loc[(d.year - yr) != 1, f"lag_{t}"] = np.nan          # lag only if the previous calendar year exists
    d["has_lag"] = d[[f"lag_{t}" for t in TARGETS_A]].notna().all(axis=1)
    return d


# --------------------------- models ---------------------------
def make_model(name: str, seed: int = 42):
    """Return a single-target sklearn-style regressor."""
    from xgboost import XGBRegressor
    from lightgbm import LGBMRegressor
    from catboost import CatBoostRegressor
    if name == "ridge":
        return make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=10.0))
    if name == "rf":
        return make_pipeline(SimpleImputer(strategy="median"),
                             RandomForestRegressor(300, min_samples_leaf=3, max_features=0.5, n_jobs=-1, random_state=seed))
    if name == "xgb":
        return XGBRegressor(n_estimators=300, learning_rate=0.05, max_depth=3, subsample=0.8, colsample_bytree=0.8,
                            min_child_weight=3, reg_lambda=5.0, random_state=seed, n_jobs=-1, verbosity=0)
    if name == "lgbm":
        return LGBMRegressor(n_estimators=300, learning_rate=0.05, num_leaves=8, min_child_samples=10, subsample=0.8,
                             subsample_freq=1, colsample_bytree=0.8, reg_lambda=5.0, random_state=seed, n_jobs=-1, verbose=-1)
    if name == "cat":
        return CatBoostRegressor(iterations=300, learning_rate=0.07, depth=4, l2_leaf_reg=5.0, random_seed=seed, verbose=0,
                                 thread_count=4)
    raise ValueError(name)


def fit_predict_multi(name: str, Xtr, Ytr, Xte, seed: int = 42):
    """Fit one model per target column (targets standardised), return predictions in original units."""
    mu, sd = Ytr.mean(0), Ytr.std(0).replace(0, 1)
    Z = (Ytr - mu) / sd
    out = {}
    if name == "cat_multi":
        from catboost import CatBoostRegressor
        m = CatBoostRegressor(iterations=600, learning_rate=0.05, depth=4, l2_leaf_reg=5.0, loss_function="MultiRMSE",
                              random_seed=seed, verbose=0, thread_count=-1)
        m.fit(Xtr, Z.values)
        P = pd.DataFrame(m.predict(Xte), columns=Ytr.columns, index=Xte.index)
        return P * sd + mu
    for c in Ytr.columns:
        m = make_model(name, seed)
        m.fit(Xtr, Z[c])
        out[c] = m.predict(Xte)
    P = pd.DataFrame(out, index=Xte.index)
    return P * sd + mu


# ---------------------- allocation engine ----------------------
def simplex_renorm(P: np.ndarray, total: float = 100.0) -> np.ndarray:
    P = np.clip(P, 0, None)
    s = P.sum(1, keepdims=True)
    s[s == 0] = 1
    return P / s * total


def bounded_projection(p: np.ndarray, lo: np.ndarray, hi: np.ndarray, total: float = 100.0) -> np.ndarray:
    """Euclidean projection of p onto {x: sum(x)=total, lo<=x<=hi} (exact, bisection on the Lagrange multiplier)."""
    a, b = (lo - p).min() - total, (hi - p).max() + total
    for _ in range(100):
        mid = (a + b) / 2
        x = np.clip(p + mid, lo, hi)
        if x.sum() > total:
            b = mid
        else:
            a = mid
    return np.clip(p + (a + b) / 2, lo, hi)


def slsqp_projection(p, lo, hi, total=100.0):
    """Same projection solved with SLSQP (used to cross-check the exact solver; this is the optimiser named in paper v1)."""
    r = minimize(lambda x: 0.5 * np.sum((x - p) ** 2), np.clip(p, lo, hi), jac=lambda x: x - p, method="SLSQP",
                 bounds=list(zip(lo, hi)), constraints=[{"type": "eq", "fun": lambda x: x.sum() - total, "jac": lambda x: np.ones_like(x)}],
                 options={"maxiter": 500, "ftol": 1e-12})
    return r.x


def allocate(P: np.ndarray, lo: np.ndarray, hi: np.ndarray, total: float = 100.0) -> np.ndarray:
    return np.vstack([bounded_projection(r, lo, hi, total) for r in P])


# --------------------------- metrics ---------------------------
def tvd(p: np.ndarray, a: np.ndarray) -> np.ndarray:
    """Total-variation distance in percentage points of the budget that would have to be moved (0-100)."""
    return 0.5 * np.abs(p - a).sum(1)


def regression_metrics(y, p) -> dict:
    y, p = np.asarray(y, float), np.asarray(p, float)
    err = p - y
    ss_res, ss_tot = (err ** 2).sum(), ((y - y.mean()) ** 2).sum()
    return {"MAE": float(np.abs(err).mean()), "RMSE": float(np.sqrt((err ** 2).mean())), "R2": float(1 - ss_res / ss_tot) if ss_tot > 0 else float("nan")}


def boot_ci(x: np.ndarray, groups: np.ndarray | None = None, n: int = 2000, seed: int = 0):
    """95% bootstrap CI of the mean; resamples countries (clusters) if groups given."""
    rng = np.random.default_rng(seed)
    x = np.asarray(x, float)
    if groups is None:
        idx = rng.integers(0, len(x), (n, len(x)))
        m = x[idx].mean(1)
    else:
        g = pd.Series(x).groupby(np.asarray(groups)).agg(["sum", "count"])
        ids = rng.integers(0, len(g), (n, len(g)))
        m = g["sum"].values[ids].sum(1) / g["count"].values[ids].sum(1)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))
