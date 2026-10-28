# Deployment, troubleshooting and operations runbook

## Local environments

**Python** (3.11 recommended):

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

**React** (Node 22 recommended):

```bash
cd frontend
npm install
npm run build
npm run dev
```

**Docker Compose:** `docker compose up --build`. Open `http://localhost:8080` and check `http://localhost:8000/api/health`.

## Provider troubleshooting

| Symptom | What to check |
|---|---|
| 401/403 on live OpenAQ | Required `OPENAQ_API_KEY`, permission, quota, API endpoint compatibility |
| No supported stations | City/time/source availability and PM2.5 `µg/m³` reporting units |
| Weather unavailable | Network, provider status, valid lat/lon, weather timestamps |
| Frontend API errors | API running, Vite proxy, browser origin, backend CORS and reverse proxy |
| Forecast appears flat | Persistence baseline intentionally repeats the latest valid daily reading |
| Missing Power BI visuals | Import `data/processed/hyderabad_synthetic_pm25.csv`; `.pbix` isn't bundled |

## Production readiness blockers

This repository is a **portfolio prototype**. Before deploying as a public service, introduce API authentication/rate limiting as appropriate, durable storage, request/worker limits, logs, uptime monitoring, robust live-feed integration tests, observability, secrets management, privacy/terms review, environmental-domain validation, licensing review, and transparent public data-source acknowledgments. Do not issue official AQI health alerts or personalized advice.

## Data provenance policy

Demo is **synthetic** throughout. Live mode fails closed if live air quality is unavailable; it does not silently serve demo results. Every display should retain units, station/source labels and timestamps. Weather is modeled context, not an in-situ pollution measurement.
