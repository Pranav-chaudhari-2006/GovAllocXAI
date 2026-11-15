"""GovAllocXAI API: reference allocation, SHAP/LIME explanations, intervals and peers from official COFOG data."""
from __future__ import annotations

import os
import threading
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict

from backend.service import COMPONENTS, FEATURES as V2_FEATURES, SDG_MAP, SHOCKS, V2Bundle, load_v2, recommend

v2_bundle: V2Bundle | None = None
v2_bundle10: V2Bundle | None = None
loading_error: str | None = None


def _load_models() -> None:
    """Fit the models in a background thread so the web server answers at once (cloud hosts need an open port within minutes)."""
    global v2_bundle, v2_bundle10, loading_error
    try:
        v2_bundle = load_v2("cofog16")
        v2_bundle10 = load_v2("cofog10")
    except Exception as exc:  # noqa: BLE001
        loading_error = repr(exc)


@asynccontextmanager
async def lifespan(_: FastAPI):
    threading.Thread(target=_load_models, daemon=True).start()
    yield


app = FastAPI(
    title="GovAllocXAI API",
    description="Reference allocation of government expenditure by COFOG function with SHAP/LIME explanations.",
    version="3.0.0",
    lifespan=lifespan,
)

frontend_origins = [o.strip() for o in os.getenv("FRONTEND_ORIGINS", "").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://localhost:4173", "http://127.0.0.1:4173", *frontend_origins],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?" r"|https://[a-zA-Z0-9-]+\.onrender\.com" r"|https://[a-zA-Z0-9-]+\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class V2Request(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    iso3: str
    year: int | None = None
    overrides: dict[str, float] = {}
    shock: Literal["recession", "stagflation", "severe_stress"] | None = None
    lime_sector: str | None = None
    panel: Literal["cofog16", "cofog10"] = "cofog16"
    total_budget_usd: float | None = None


@app.get("/api/v2/health")
def v2_health() -> dict[str, object]:
    return {"status": "ok" if (v2_bundle is not None and v2_bundle10 is not None) else ("error" if loading_error else "initializing"), "components": COMPONENTS, "features": V2_FEATURES,
            "training_rows": 0 if v2_bundle is None else len(v2_bundle.panel),
            "panels": {"cofog16": "16 COFOG functions, Eurostat+OECD, 36 economies", "cofog10": "10 COFOG divisions, Eurostat+OECD+IMF, 85 economies"},
            "shocks": list(SHOCKS), "sdg_map": SDG_MAP}


@app.get("/api/v2/economies")
def v2_economies() -> list[dict[str, object]]:
    if v2_bundle is None:
        raise HTTPException(status_code=503, detail="The models are still starting up.")
    g = v2_bundle.master.groupby(["iso3", "country"]).year.max().reset_index()
    covered = set(v2_bundle.panel.iso3)
    return [{"iso3": r.iso3, "country": r.country, "latest_feature_year": int(r.year), "has_official_cofog_history": r.iso3 in covered}
            for r in g.itertuples()]


@app.post("/api/v2/recommend")
def v2_recommend(request: V2Request) -> dict[str, object]:
    if v2_bundle is None:
        raise HTTPException(status_code=503, detail="The models are still starting up.")
    try:
        bundle = v2_bundle10 if request.panel == "cofog10" else v2_bundle
        if bundle is None:
            raise HTTPException(status_code=503, detail="The models are still starting up.")
        return recommend(bundle, request.iso3, request.year, request.overrides, request.shock, request.lime_sector, 5, request.total_budget_usd)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
