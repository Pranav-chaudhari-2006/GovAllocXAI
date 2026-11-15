import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture(scope="module")
def client():
    import time
    with TestClient(app) as c:
        for _ in range(240):                       # models are fitted in a background thread
            if c.get("/api/v2/health").json()["status"] == "ok":
                break
            time.sleep(2)
        yield c


def test_v2_recommend_sums_to_100_and_has_shap(client):
    r = client.post("/api/v2/recommend", json={"iso3": "DEU", "year": 2023})
    assert r.status_code == 200
    j = r.json()
    assert abs(j["sum_check"] - 100) < 1e-6
    assert len(j["components"]) == 17
    assert all(len(c["top_shap"]) == 5 for c in j["components"])
    assert abs(sum(c["recommended_share_pct"] for c in j["components"]) - 100) < 1e-6


def test_v2_shock_changes_recommendation_and_lime_is_returned(client):
    base = client.post("/api/v2/recommend", json={"iso3": "DEU", "year": 2023}).json()
    stressed = client.post("/api/v2/recommend", json={"iso3": "DEU", "year": 2023, "shock": "severe_stress", "lime_sector": "health"}).json()
    assert [c["recommended_share_pct"] for c in base["components"]] != [c["recommended_share_pct"] for c in stressed["components"]]
    assert "lime" in stressed and len(stressed["lime"]["features"]) > 0


def test_v2_unknown_economy_and_feature(client):
    assert client.post("/api/v2/recommend", json={"iso3": "ZZZ"}).status_code == 404
    assert client.post("/api/v2/recommend", json={"iso3": "DEU", "overrides": {"not_a_feature": 1.0}}).status_code == 400


def test_v2_applicability_present(client):
    j = client.post("/api/v2/recommend", json={"iso3": "IND", "year": 2022}).json()
    assert set(j["applicability"]) >= {"novelty_score", "percentile_among_training_economies", "status"}


def test_v2_wide_panel_serves_developing_economy(client):
    j = client.post("/api/v2/recommend", json={"iso3": "IND", "year": 2022, "panel": "cofog10"}).json()
    assert j["panel"] == "cofog10" and len(j["components"]) == 10
    assert abs(j["sum_check"] - 100) < 1e-6 and j["training_economies"] >= 80


def test_v2_total_budget_and_amounts(client):
    j = client.post("/api/v2/recommend", json={"iso3": "DEU", "year": 2023, "total_budget_usd": 1.0e12}).json()
    assert j["total_budget"]["source"] == "user-supplied"
    assert abs(sum(c["amount_usd"] for c in j["components"]) - 1.0e12) < 1e3
    k = client.post("/api/v2/recommend", json={"iso3": "DEU", "year": 2023}).json()
    assert 10 < k["total_budget"]["predicted_total_expenditure_pct_gdp"] < 90


def test_v2_peers_and_intervals(client):
    j = client.post("/api/v2/recommend", json={"iso3": "DEU", "year": 2023}).json()
    assert len(j["similar_economies"]) == 5 and all(p["iso3"] != "DEU" for p in j["similar_economies"])
    if j["intervals"]:
        c = j["components"][0]
        assert c["interval_90_pp"][0] <= c["recommended_share_pct"] <= c["interval_90_pp"][1]
