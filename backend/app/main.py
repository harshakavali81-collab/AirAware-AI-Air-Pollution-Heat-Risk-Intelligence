"""FastAPI application. All responses carry source-mode information."""
import os
from functools import lru_cache
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from src.airaware.config import CITIES, settings
from src.airaware.ingestion.openaq_client import AirDataError
from backend.app import service

app = FastAPI(title="AirAware AI API", version="1.0.0", description="Air quality and illustrative heat exposure; source provenance included")
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET"], allow_headers=["*"])


def get_snapshot(city):
    try:
        return service.snapshot(city)
    except (AirDataError, ValueError) as exc:
        raise HTTPException(status_code=503 if isinstance(exc, AirDataError) else 422, detail=str(exc)) from exc


@app.get("/api/health")
def health():
    return {"status": "ok", "mode": settings().mode}


@app.get("/api/cities")
def cities():
    return {"cities": list(CITIES.keys())}


@app.get("/api/overview")
def overview(city: str = Query("Hyderabad")):
    return service.overview(get_snapshot(city))


@app.get("/api/stations")
def stations(city: str = Query("Hyderabad")):
    s = get_snapshot(city)
    return {"city": city, "mode": s["mode"], "stations": service.station_summary(s), "notice": s["notice"]}


@app.get("/api/trends")
def trends(city: str = Query("Hyderabad"), days: int = Query(30, ge=7, le=120)):
    s = get_snapshot(city)
    return {"city": city, "mode": s["mode"], "trends": service.trends(s, days), "units": "µg/m³", "notice": s["notice"]}


@app.get("/api/forecast")
def forecast(city: str = Query("Hyderabad"), days: int = Query(7, ge=1, le=14)):
    return service.forecast_data(get_snapshot(city), days)


@app.get("/api/quality")
def quality(city: str = Query("Hyderabad")):
    return service.quality(get_snapshot(city))
