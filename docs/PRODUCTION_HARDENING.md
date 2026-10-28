# Production hardening — verified code, external activation pending

**Date:** 2026-10-28. The changes below improve a demonstrator; they do not turn the project into an independently verified air-quality or public-safety service.

## Protection and reliability implemented

| Control | Implementation | Verification |
|---|---|---|
| Readiness vs liveness | `/api/health` verifies that the process responds; `/api/ready` checks required runtime configuration without pretending to contact providers | Offline API tests |
| API key handling | OpenAQ `X-API-Key` is sent from Python only, never bundled with JavaScript; `.env` is gitignored | Source/test inspection; no real key provided |
| OpenAQ quota protection | Latest PM2.5 results are cached for ten-minute buckets, while failed lookups still return errors; daily observations are cached separately | Unit tests with mock upstream |
| Browser/API headers | `nosniff`, `DENY` frames, strict referrer policy, no-store for API responses | API tests |
| Strict source provenance | Demo/live data never silently interchange; OpenAQ latest is labeled *last reported*, not a complete ingestion stream | API tests and docs |
| Chronological evaluation | Expanding-window model evaluation over disjoint calendar periods, vs prior-observation persistence | Offline synthetic evaluation tests |
| Data coverage gate | Missing calendar days remain gaps, and tests reject sparse or insufficient history | Offline unit tests |
| Source restriction | CSV inputs containing "synthetic" / "demo" / "fabricated" cannot silently pass as real | Offline unit tests |

These are useful safeguards, **not** a complete threat model. Before using the site with significant public traffic, add hosted edge rate limiting, uptime checks, centrally managed secrets, artifact provenance, container vulnerability scanning and regular dependency updates. Render's free filesystem is not durable storage for long-term data. Verify upstream provider licenses and attribution.

## Configure and test a live instance

1. Link this GitHub repository to a Render Blueprint (`render.yaml`). The **account owner** must authorize creation of the service; committing YAML does not start hosting.
2. Deploy with `AIR_DATA_MODE=demo` to confirm the React UI and API work together. In the hosting dashboard, inspect the *actual* assigned hostname before sharing any URL.
3. Set `OPENAQ_API_KEY` as an environment secret. Switch `AIR_DATA_MODE=live` only after you have verified API access and sensor coverage. Never commit the key.
4. Call `/api/health`, `/api/ready`, `/api/overview?city=Hyderabad`, `/api/latest?city=Hyderabad`. Check the timestamps, station count, source, units and cache behavior. **Readiness is not upstream availability.**
5. Run the real-source backtest and verify the resulting `data_mode`, provenance metadata and reporting windows before publicly discussing model results. Independently validate measurements and out-of-period behavior.
6. Open `powerbi/AirAwareReport/AirAware.pbip` in Power BI Desktop, verify it refreshes and save/export a `.pbix` through Power BI Desktop if required. A tested PBIP file is not evidence of a validated PBIX package.

### Real-data evaluation

```bash
# Only once a private OPENAQ_API_KEY has been configured locally
python -m scripts.live_backtest --city Hyderabad --days 180 --output data/processed/live_openaq_pm25.csv
python -m src.airaware.models.rolling_backtest \
  --csv data/processed/live_openaq_pm25.csv \
  --city Hyderabad --output data/processed/live_rolling_backtest.json
```

The script will refuse low-coverage or short-duration data; that is a legitimate result, not a failure to hide. Even when it runs successfully, the output is **offline statistical backtesting, not independently verified real-world forecasting skill**.

Synthetic demonstration for reproducibility:

```bash
python -m src.airaware.models.rolling_backtest \
  --csv data/processed/hyderabad_synthetic_pm25.csv \
  --city Hyderabad --allow-synthetic \
  --output data/processed/rolling_backtest_synthetic_example.json
```

## Deployment acceptance criteria

- A real public domain and HTTPS return a working UI and `/api/health`.
- Production secrets are stored as hosted environment variables, and do not appear in GitHub history or browser bundles.
- Live PM2.5 responses show source, station-specific timestamps, coverage, parameter, units and data quality limitations; missing data is not filled with samples.
- Errors and upstream 429s are visible and safely handled; public usage has provider quota protection.
- Real-data model validation is independently inspected before any claim of forecast accuracy.
- Power BI report opens, refreshes and displays the expected fields in Desktop; a `.pbix` exists only after an actual save/export there.

All items requiring an external service must be checked in that service, not inferred from repository files or CI build success.
