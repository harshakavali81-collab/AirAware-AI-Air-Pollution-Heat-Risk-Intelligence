# Real-world forecast validation protocol (not yet executed on authenticated data)

**Live source auth requirement:** [OpenAQ v3](https://docs.openaq.org/api) uses a `X-API-Key` HTTP header. OpenAQ daily aggregates are not real-time readings. The API client already sets the header on requests, and `scripts/live_backtest.py` provides an end-to-end ingestion → provenance → evaluation path.

## Reproducible procedure
1. Obtain your own key, place it only in `.env` or hosting secrets: `OPENAQ_API_KEY=...`. Never commit it.
2. Run `python -m scripts.live_backtest --city Hyderabad --days 120 --output data/processed/live_openaq_pm25.csv` from a machine with network connectivity.
3. Review `live_openaq_pm25.metadata.json`: `mode`, retrieval timestamp, first/last measurement date, actual reporting stations, PM2.5 units, licensing, and source metadata.
4. Compare random forest with a one-day lag persistence baseline on the last 20% of the calendar-ordered dates. Only compare **same horizon**; preserve chronological ordering. Report MAE/RMSE in µg/m³.
5. Do not advertise model accuracy unless real source rows exist and the file's provenance/units/license can be inspected. Repeat with rolling-origin temporal folds, seasonal holdouts and station-level controls before making a claim of robust geographic generalization.

## Operational notes
- Key errors, rate limits and unavailable stations are explicit failures, never silent synthetic fallbacks.
- Station count is not the same as geographic representativeness. Results are biased by monitoring placement and sensor outages.
- Daily means from multiple station sensors can undercount high-frequency events; the forecast endpoint stays a non-trained persistence baseline.
- Do not confuse Open-Meteo weather-grid predictions with measured PM2.5; no personalized health guidance.
- Use reasonable request rates, monitor your OpenAQ quotas and follow source licenses.

**Status:** No verified authenticated API call or validated real-world error score is included in the repository. Evaluation code and tests are available but need external credentialed data and independent review.
