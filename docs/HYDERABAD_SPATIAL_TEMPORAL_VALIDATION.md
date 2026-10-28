# Hyderabad 2024 unseen-station, future-window evaluation

**Purpose.** This complements the existing recorded-source 2024 Hyderabad time-separated city-average backtest with a stronger *out-of-station plus future-date* evaluation. It is an exploratory statistical generalization check, **not** production forecasting validation, current OpenAQ ingestion, sensor calibration or health advice.

## Method and leakage controls

1. Download XKDR Forum's 2024 Hyderabad station-day PM2.5 data compiled from CPCB CAAQM stations, using the XKDR-published demonstration API token. Record CSV digest and provider metadata. This is separate from OpenAQ v3 credentials.
2. Parse PM2.5 units conservatively, reject dates outside 2024 and invalid station IDs, and deduplicate station-days.
3. Use a fixed **2024-10-01** date cutoff. Eligible evaluation stations must have at least 35 days of reporting *after* that date. From that predeclared coverage-eligible group, hold out the first floor(n/5) stations by SHA256 hash order of station ID. This makes holdout selection deterministic, though the coverage filter itself uses future reporting availability.
4. Train Random Forest **only on remaining stations before October 1**, without station-ID features. Inputs are the *previous calendar day* mean PM2.5 of known training stations and known calendar-phase values. Use a calendar frequency reindex so missing days cannot masquerade as day-1 lag. Compare against the same previous-day training-network mean as a naive baseline.
5. Evaluate on the never-trained stations dated **October–December 2024**. The test stations' target values are never used in constructing features. Daily training-network readings in the test period are allowed as an operationally observable previous-day predictor.
6. Export per-station MAE, RMSE and row counts plus provenance metadata. Keep results in `reports/hyderabad_cpcb_spatial_temporal_2024.json` only after a successful remote observed-source workflow run.

## Source and scope

- [XKDR Forum India Air Quality Database](https://airquality.xkdr.org/) / CPCB CAAQM, 2024 historical records.
- [Dedicated GitHub Actions workflow](../.github/workflows/india-spatial-temporal-generalization.yml) and [benchmark script](../scripts/india_spatial_temporal_backtest.py).
- The task is **station-level transfer**; its errors are not directly comparable with the prior *city-average* 2024 forecast benchmark. Station geographic representativeness, calibration and drift are not independently audited.
- There is **no model promotion**. Never interpret this historical score as evidence of current India forecast skill or operational alerts.

## Acceptance

A passing CI run must demonstrate an authenticated download from the historical XKDR endpoint with the published demonstration key, a nonempty CSV with recorded digest, disjoint dates and stations, per-station test sample sizes and realistic metrics. The owner still needs real 2026 data, OpenAQ credentials and a hosted service for live operations; a rigorous historical holdout does not replace those steps.
