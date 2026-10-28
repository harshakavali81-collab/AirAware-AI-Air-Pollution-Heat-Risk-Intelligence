# Production completion matrix (updated 2026-10-28)

| Workstream | Implemented & locally checked | Requires real user credentials / external verification |
|---|---|---|
| Full-stack hosting | Multi-stage React + FastAPI Dockerfile, single-origin serve, Render Blueprint, health check | Create Render web service in your own account, verify public domain, secure rate limits, inspect logs, monitor uptime |
| OpenAQ v3 API | `X-API-Key` backend client, live source mode, explicit errors, data-provenance export script | Obtain API key, run authenticated API call, inspect sensor coverage and provider licenses |
| Real-world ML evaluation | Chronological model vs persistence, validation instructions, real-data ingestion-to-backtest CLI, unit tests | Collect licensed real observations with sufficient history; inspect station representativeness and seasonal out-of-time validation |
| Power BI | Editable PBIP semantic model (TMSL) + PBIR pages/visuals with synthetic sample | Open and refresh in Microsoft Power BI Desktop, export `.pbix` if needed, optionally publish to Power BI Service with approved license |

**No source code is proof of completed remote infrastructure.** The GitHub repository is the codebase; a checked-in Render Blueprint alone is not a deployed service. Avoid claiming live measured data or validated forecasting accuracy before obtaining real results.
