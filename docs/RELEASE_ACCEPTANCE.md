# Production release acceptance checklist

**Status: NOT ACCEPTED FOR PUBLIC LIVE OPERATIONS** as of 2026-10-28. The checked-in Dockerfile, Render blueprint, and passing CI establish build readiness, **not** a running public service.

## A. Code and artifact integrity (automated)

1. `python -m pytest -q` passes Python tests.
2. `python -m scripts.verify_powerbi_project` parses the source-controlled PBIP, semantic model, report pages, and visual references. **This only verifies structure**; Microsoft Power BI Desktop is still mandatory for visual compatibility, refresh, and `.pbix` export.
3. `npm install --prefix frontend` then `npm run build --prefix frontend` produces static frontend assets.
4. Full-stack Docker CI test passes `/api/health` on a local container.

## B. Public deployment (requires owner to activate Render)

1. In your own Render account create a Blueprint from this GitHub repository's `render.yaml`.
2. Start with `AIR_DATA_MODE=demo`, configure HTTPS, review cost, monitoring, rate limiting, logs, and recovery.
3. Run `python -m scripts.check_deployment --url https://YOUR-REAL-HOST` or manually dispatch **Manual public production smoke test** with the URL.
4. Verify the browser's HTML and API requests originate from the same correct host and show **DEMO** prominently; do not confuse a GitHub Pages portfolio with the FastAPI backend deployment.
5. Record the exact verified domain, deployment time, commit hash, API response, and monitoring policy. Do not publish an unverified URL.

## C. Real OpenAQ ingestion (requires owner API credentials)

1. Generate OpenAQ credentials from the service, store `OPENAQ_API_KEY` as a Render secret. Never commit keys or log response headers.
2. Select `AIR_DATA_MODE=live` only when endpoints and station coverage respond successfully.
3. Dispatch the production smoke workflow with `require_live=true` and inspect timestamps, unit, station coverage, geographic relevance, aggregation, quality flags, and provider terms. A nonempty reading is not evidence of scientific calibration or forecasting accuracy.
4. Run `python -m scripts.live_backtest --city Hyderabad --days 120` with adequate coverage, and perform independent temporal/spatial domain-expert review.

## D. Modeling and data trust

- Existing observed historical Beijing benchmark (2013–2017): 10 folds, persistence mean-fold MAE **42.4398** vs Random Forest **42.6768** µg/m³. The candidate did **not** beat the baseline. This is **not a validated Hyderabad/India forecast**.
- Do not describe the heat indicator as medical advice, scientific heat-alert certification, or validated local risk guidance.
- Require independent model review, versioned feature definition, representative location/time holdouts, drift monitoring, and model rollback protocol before promotion.

## E. Power BI owner acceptance

1. Open `powerbi/AirAwareReport/AirAware.pbip` in supported Power BI Desktop for Windows.
2. Verify both pages and five visuals; refresh the synthetic model, inspect type conversions and source labels, then save a `.pbix` copy as appropriate.
3. Capture Desktop version, date, screenshots, refresh outcome, warnings, and checksums of exported artifacts.
4. Do not mark native `.pbix` verified until the above is performed on real Power BI Desktop.

## Current conclusion

The source is portfolio-ready and CI-tested. Deployment, authenticated current-location readings, operational forecasting validation, and native Power BI Desktop verification still require external accounts, private credentials, or external Windows desktop software. This repository cannot bypass those requirements.

## Deployment gate upgrade (2026-10-28)

- The README has a verified official-format Render deploy-button link. Owner authorization is still required.
- Render Blueprint sets `autoDeployTrigger: checksPass`, rather than deploying every commit before CI finishes.
- The manual `production-smoke.yml` workflow accepts a measured timestamp freshness threshold (`max_reading_age_minutes`, default 2880) and a minimum number of distinct stations (`min_stations`, default 1).
- The checker validates `mode=live`, the UTC measurement timestamp, measurement units, numeric PM2.5 bounds, source identity, and geographic station count. **No API key is embedded in the workflow.**
- A passing operational gate does not establish a regulator-grade AQI, a calibrated forecast, or a validated heat alert.
