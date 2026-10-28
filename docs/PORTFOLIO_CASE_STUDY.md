# AirAware AI — Air Pollution & Heat Risk Intelligence

**Role:** Full-stack data and ML project | **Stack:** Python, Pandas, SQL/SQLite, scikit-learn, FastAPI, React, Recharts, Leaflet, OpenAQ v3 and Open-Meteo.

## The challenge
Pollution data is difficult to interpret when monitoring sites report on different dates, geographic coverage is uneven and forecasts are mistaken for measurements.

## Solution
AirAware presents per-city PM2.5 historical aggregates, hypothetical/demo vs real-source labels, monitored-location maps, data freshness indicators and an independently marked short-horizon baseline. It adds weather context and a clearly caveated apparent-temperature exposure band.

## Engineering decisions
- Built repeatable synthetic demo data so reviewers can explore the full app without credentials.
- Added credentialed OpenAQ v3 connectors with strict units and provenance instead of inventing readings on failed API calls.
- Used time-split MAE/RMSE comparisons and lagged features that do not contain future targets.
- Designed a self-contained React interface and optional CSV/SQLite/Power BI data path.

## Results
Reproducible API tests and an offline train/evaluate benchmark on **synthetic data**. No real-world forecast accuracy, user engagement uplift, or deployed-user benefits claimed. This project is separate from the linked OpenKit Air Aware case study; no affiliation or borrowed 93% result.

## Future work
Authenticated station snapshots, proper historical backtesting on real data, heat-risk validation against official guidance, station-level maps and production monitoring.
