# Full-stack deployment: developer / owner activation checklist

## What is actually built
The root `Dockerfile` is now a multi-stage build. Node builds the React/Vite dashboard and Python/FastAPI serves the compiled dashboard and `/api/*` from **one origin**. `render.yaml` is a Render Blueprint for a managed web service. `GET /api/health` is the health check.

## Deploy on Render (requires your Render account)
1. Open [Render Blueprints](https://dashboard.render.com/blueprints) and link this GitHub repository. Approve the `render.yaml` blueprint. Do **not** paste any secrets into code or GitHub files.
2. Start in `AIR_DATA_MODE=demo`. Once the site is deployed, verify `/api/health`, `/api/overview?city=Hyderabad` and the dashboard. Demo means synthetic readings.
3. In **Render dashboard → your web service → Environment**, save `OPENAQ_API_KEY` as a secret. Change `AIR_DATA_MODE` to `live`, then redeploy. Missing or invalid keys produce a clear API error; demo values never silently replace real data.
4. Verify the first live response has `mode=live`, source attribution, sensible station count, units, and timestamps before publicizing live monitoring.
5. Before making this a serious production service, use a paid instance, reverse-proxy rate limiting, a durable database, pinned dependencies, monitoring, backups, quotas, provider terms/license review and a domain-level security review. Render free services are for evaluation/hobby use and may sleep / reset filesystem state.

## Test locally
```sh
docker build -t airaware-ai .
docker run --rm -p 8000:8000 --env AIR_DATA_MODE=demo airaware-ai
# browser: http://localhost:8000/
# API: http://localhost:8000/api/health
```

A working `render.yaml` does NOT create a service automatically: activation requires account permission and approval. No public backend URL is claimed until checked. This is an environmental data explorer, not an official public safety system.

**October 28 update:** `/api/ready` is a configuration-only check (live mode without a key returns 503); `/api/health` remains a liveness check. Latest-sensor calls are cached in 10-minute windows to reduce OpenAQ quota use. The Blueprint no longer hardcodes a guessed Render domain; React and the API share the same origin by default. See [PRODUCTION_HARDENING.md](PRODUCTION_HARDENING.md).
