# Historical observed PM2.5 evaluation — independent public benchmark

**Scope:** This benchmark concerns **Beijing, China, 2013–2017**. It does not measure 2026 air quality, does not exercise the OpenAQ API, and **does not independently validate Indian city forecasts**. Its purpose is to test the forecasting pipeline against genuinely recorded historical PM2.5 observations rather than synthetic examples.

## Data attribution and licensing

- Dataset: [Beijing Multi-Site Air Quality](https://archive.ics.uci.edu/dataset/501/beijing+multi+site+air+quality+data) (UCI dataset 501)
- Citation: Song Xi Chen (2017), *Beijing Multi-Site Air Quality*, UCI ML Repository, [doi:10.24432/C5RK5G](https://doi.org/10.24432/C5RK5G)
- Original observations: Beijing Municipal Environmental Monitoring Center, 12 monitoring sites, 2013-03-01 to 2017-02-28
- License: [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/). Preserve source citation and license when redistributing derivatives.
- Unit: PM2.5, µg/m³. Missing raw values are dropped, **not invented**.

## Reproduce in GitHub Actions

Workflow: [`.github/workflows/historical-observation-benchmark.yml`](../.github/workflows/historical-observation-benchmark.yml). It downloads the official ZIP *directly from UCI* and records the SHA256 digest, station count, chronological fold counts, and separately scored persistence and Random Forest MAE. Run automatically on changes to the workflow/evaluation code or manually via the GitHub Actions page. Download its JSON workflow artifact to see individual fold results; do not claim the report exists until that run succeeds.

Local one-liner (internet required):

```bash
python -m pip install -e '.[dev]'
python -m scripts.uci_beijing_benchmark --download-official --output reports/uci_beijing_historical.json
```

Or with a downloaded ZIP `python -m scripts.uci_beijing_benchmark --archive /path/to/uci.zip --output reports/offline_validation.json`. The offline ZIP is **not** authenticated as the official data, and the report explicitly identifies its provenance as unverified.

### Method

1. Parse the source's 12 hourly station CSVs (including its nested ZIP layout). Convert hourly observations into local calendar-day station averages. Keep only actual nonnegative PM2.5 data. Never interpolate missing observations.
2. Compute one equal-weight city-wide mean from available station daily means; results may be biased by changing station availability.
3. Require at least 365 observed days and 90% local-calendar day coverage. Use a minimum ~850-day initial history, then disjoint 60-day test windows.
4. Score an expanding-training Random Forest against the lag-one persistence benchmark on the **same** test dates, preserving one-day-ahead semantics. Predictors include only lagged observed PM2.5 and known weekday; no future measurements.
5. Report **MAE in µg/m³**, per-fold scores and archive digest. No confidence intervals, external station transfer, calibration or independent scientific accreditation is claimed.

## Interpret with caution

- **Real historical source, not operationally validated:** It establishes whether code can be evaluated against an attributed observational dataset. It does not prove the model can forecast local pollution in a new city, season, year, sensor network, or different resolution.
- No current Hyderabad/Delhi observations appear in the report. To evaluate them use `scripts/live_backtest.py` with a private OpenAQ key, then independent station/season holdouts and source permissions.
- Results are exploratory and must not be used for medical, regulatory, emergency or individualized recommendations.
- The GitHub Action may fail if UCI is temporarily unavailable or blocks download: an upstream availability failure is not a model result and must be disclosed.
