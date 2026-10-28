# Deployment guide

## Local Docker

```bash
cp .env.example .env
# edit AIR_DATA_MODE=live and OPENAQ_API_KEY=... only after obtaining credentials
docker compose up --build
```

Visit http://localhost:8080. FastAPI is internal to the Compose network, reachable from frontend Nginx at `/api/`.

## Platform deployment

Deploy the Python Dockerfile as an API service with `AIR_DATA_MODE=live`, `OPENAQ_API_KEY` and allowlisted `CORS_ORIGINS`. Deploy the frontend separately as a static Vite app (`frontend/` build) and set `VITE_API_BASE=https://YOUR-API-ORIGIN`. Ensure the frontend base includes NO trailing slash. Use HTTPS and a durable storage volume if using SQLite snapshots.

Vercel can host the static frontend. A continuously running Python service plus persistent database is separate infrastructure; this repository does not automatically create a Vercel account or provision services.

Before public production: request handling and retry policy, licensed provider data usage, OSM tile policy, secure logs, dependency review, health checks, queueing/backoff and observability. Do not claim deployment until URLs and service health are verified.
