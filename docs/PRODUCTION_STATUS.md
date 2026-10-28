# Production completion matrix (updated 2026-10-28)

| Workstream | Implemented & locally checked | Requires real user credentials / external verification |
|---|---|---|
| Full-stack hosting | Multi-stage React + FastAPI Dockerfile, single-origin serve, Render Blueprint, health check | Create Render web service in your own account, verify public domain, secure rate limits, inspect logs, monitor uptime |
| OpenAQ v3 API | `X-API-Key` backend client, live source mode, explicit errors, data-provenance export script | Obtain API key, run authenticated API call, inspect sensor coverage and provider licenses |
| Real-world ML evaluation | Chronological model vs persistence, validation instructions, real-data ingestion-to-backtest CLI, unit tests | Collect licensed real observations with sufficient history; inspect station representativeness and seasonal out-of-time validation |
| Power BI | Editable PBIP semantic model (TMSL) + PBIR pages/visuals with synthetic sample | Open and refresh in Microsoft Power BI Desktop, export `.pbix` if needed, optionally publish to Power BI Service with approved license |

**No source code is proof of completed remote infrastructure.** The GitHub repository is the codebase; a checked-in Render Blueprint alone is not a deployed service. Avoid claiming live measured data or validated forecasting accuracy before obtaining real results.

## Additional implementation (October 28)

- Confirmed previous GitHub Actions `main` run completed successfully. A successful CI build confirms source checks and container smoke tests, **not** public hosting.
- Added `/api/ready`, security headers, and 10-minute caching of OpenAQ latest measurements with offline tests.
- Added `src/airaware/models/rolling_backtest.py` for disjoint expanding evaluation windows, missing-day gating, and explicit synthetic-source detection. Synthetic example scores are not real-world evidence.
- No credentials or Power BI Desktop environment were available to independently validate live API access or export `.pbix`.

Detailed controls and owner acceptance checklist: [Production hardening](PRODUCTION_HARDENING.md).

## Independent historical dataset evaluation upgrade (October 28, 2026)

The new [UCI Beijing historical-observation benchmark](HISTORICAL_OBSERVATION_BENCHMARK.md) uses an official public *observed* 2013–2017 dataset (12 sites, CC BY 4.0) to exercise the expanding-window evaluation pipeline with provenance and test-period metrics. Its GitHub workflow downloads the official archive and publishes a limited-lifetime JSON artifact. Do not state that the download, model backtest, or benchmark run succeeded unless the [workflow](../.github/workflows/historical-observation-benchmark.yml) has completed successfully.

This is independent historical **Beijing** benchmarking, **not** the outstanding authenticated OpenAQ data for India or deployment validation. The hosted Render API, OpenAQ key, and Power BI Desktop validation still require owner-provided external access. The [HTTPS post-deployment check](../scripts/check_deployment.py) exists to verify a real URL after deployment.


## Latest verification additions

- CI now checks Power BI PBIP source structure. Desktop verification and `.pbix` export require Windows Power BI Desktop.
- A manually triggered HTTPS smoke workflow is available; it requires an already-activated public host and does not provision Render.
- [Release acceptance checklist](RELEASE_ACCEPTANCE.md) records exact outstanding external operations and evidence before production claims can change.
