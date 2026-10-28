"""FastAPI application. All responses carry source-mode information."""
import os
from pathlib import Path
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from src.airaware.config import CITIES, settings
from src.airaware.ingestion.openaq_client import AirDataError
from backend.app import service

app = FastAPI(title="AirAware AI API", version="1.0.0", description="Air quality and illustrative heat exposure; source provenance included")
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET"], allow_headers=["*"])


@app.middleware("http")
async def public_response_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-Frame-Options"] = "DENY"
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    return response


def get_snapshot(city):
    try:
        return service.snapshot(city)
    except (AirDataError, ValueError) as exc:
        raise HTTPException(status_code=503 if isinstance(exc, AirDataError) else 422, detail=str(exc)) from exc


@app.get("/api/health")
def health():
    # Liveness is not proof that live upstream sources or the model are healthy.
    return {"status": "ok", "mode": settings().mode, "scope": "process_liveness_only"}


@app.get("/api/ready")
def ready(response: Response):
    """Configuration readiness, not an independent upstream connectivity test."""
    cfg = settings()
    if cfg.mode == "live" and not cfg.key:
        response.status_code = 503
        return {"status": "not_ready", "mode": cfg.mode, "reason": "openaq_key_not_configured"}
    return {"status": "ready", "mode": cfg.mode,
            "scope": "configuration_only; upstream service not checked"}


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


@app.get("/api/latest")
def latest(city: str = Query("Hyderabad")):
    # Deliberately distinguish source's most recent measurement from real-time AQI.
    from backend.app.service import cached_latest
    cfg = settings()
    if city not in CITIES:
        raise HTTPException(status_code=422, detail="Unsupported city")
    if cfg.mode == 'demo':
        return {'city':city, 'mode':'demo', 'readings':[], 'notice':'No live readings in synthetic demo mode.'}
    try:
        readings = cached_latest(city, cfg.key, int(__import__("time").time() // 600))
    except AirDataError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {'city':city,'mode':'live','readings':readings,'notice':'Latest reported sensor values; station timestamps can be stale and do not guarantee complete time-series ingestion.'}


@app.get("/api/quality")
def quality(city: str = Query("Hyderabad")):
    return service.quality(get_snapshot(city))


# Built frontend is packaged by the multi-stage Dockerfile. Local API-only development
# continues working when frontend/dist has not been built.
DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="web-assets")

    @app.get("/", include_in_schema=False)
    @app.get("/{path:path}", include_in_schema=False)
    def frontend(path: str = ""):
        if path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        return FileResponse(DIST / "index.html")
