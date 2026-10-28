# Verified historical Beijing PM2.5 backtest result

**This is a real recorded-source historical benchmark, NOT a live Hyderabad/India air quality forecast, deployed OpenAQ API, clinical advice, or a production model validation.**

- GitHub Actions run (passed): https://github.com/harshakavali81-collab/AirAware-AI-Air-Pollution-Heat-Risk-Intelligence/actions/runs/40649009601
- Source: [UCI Beijing Multi-Site Air Quality](https://archive.ics.uci.edu/dataset/501/beijing+multi+site+air+quality+data), [DOI 10.24432/C5RK5G](https://doi.org/10.24432/C5RK5G), CC BY 4.0.
- Dataset: March 2013–February 2017; **420,768** hourly rows, **12** monitoring sites, **8,739** missing hourly PM2.5 values, **17,467** nonmissing station-days.
- SHA256 downloaded official UCI ZIP: `b04da438b2f331ac0ffd45aebdfec0d20d2367feb5f6948c4b1f7ce1191e33c4`
- Evaluation: **10** nonoverlapping calendar-window folds, expanding history, lag-only one-day-ahead PM2.5 prediction; units µg/m³.

## Historical out-of-time mean-fold error

| Predictor | MAE (µg/m³; lower better) |
|---|---:|
| Last-day persistence baseline | **42.4398** |
| Random Forest candidate | 42.6768 |

The Random Forest model's mean-fold MAE was **0.2370 µg/m³ higher (worse)** than persistence. **Do not deploy this candidate as a performance improvement** on the evidence available. Per-fold results, RMSE and source metadata appear in [`reports/uci_beijing_historical.json`](../reports/uci_beijing_historical.json).

## Per-fold comparison

| Train end | Test dates | Persistence MAE | Random Forest MAE |
|---|---|---:|---:|
| 2015-07-05 | 2015-07-06 to 2015-09-03 | 22.47 | 25.71 |
| 2015-09-03 | 2015-09-04 to 2015-11-02 | 35.49 | 39.19 |
| 2015-11-02 | 2015-11-03 to 2016-01-01 | 71.71 | 70.64 |
| 2016-01-01 | 2016-01-02 to 2016-03-01 | 35.14 | 37.43 |
| 2016-03-01 | 2016-03-02 to 2016-04-30 | 44.37 | 44.27 |
| 2016-04-30 | 2016-05-01 to 2016-06-29 | 26.69 | 26.98 |
| 2016-06-29 | 2016-06-30 to 2016-08-28 | 26.66 | 25.94 |
| 2016-08-28 | 2016-08-29 to 2016-10-27 | 37.83 | 34.24 |
| 2016-10-27 | 2016-10-28 to 2016-12-26 | 60.53 | 60.89 |
| 2016-12-26 | 2016-12-27 to 2017-02-24 | 63.51 | 61.49 |

## Interpretation and limitations

- The benchmark proves the code fetched an attributed observational archive from UCI in CI and performed a reproducible historical time-separated comparison. Its reported numbers do **not** validate future season/city/site transfer, explain causal pollution drivers or confirm OpenAQ real-time provider access.
- The historical aggregate combines only available station-days and the source station network; changing station coverage may bias the city average. A true operational system needs independently reviewed coverage QA, sensor provenance, calibration and holdouts across new locations/time periods.
- Free Render deployment, `AIR_DATA_MODE=live`, private OpenAQ key, and Power BI Desktop report export remain **owner-dependent and unverified**.
