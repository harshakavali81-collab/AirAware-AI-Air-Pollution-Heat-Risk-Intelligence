# Project workflow and pipeline

![Workflow](../assets/project-workflow.png)

## Data-to-insight flow

```mermaid
flowchart TD
    A{AIR_DATA_MODE} -->|demo| B[Seeded synthetic station-day records]
    A -->|live| C[OpenAQ v3 PM2.5 with server-side API key]
    C --> D[Validation: dates, units, missingness, source]
    B --> D
    D --> E[Normalized UTC timestamps and station metadata]
    E --> F[Daily aggregation and coverage indicators]
    F --> G[FastAPI read-only endpoints]
    G --> H[React / Leaflet / Recharts UI]
    F --> I[Optional SQLite and CSV export]
    I --> J[Power BI import example]
    F --> K[Offline time-separated ML experiment]
    K --> L[Baseline vs Random Forest MAE/RMSE]
    M[Open-Meteo grid-model fields] --> G
```

`AIR_DATA_MODE=live` is **never** substituted with synthetic measurements on provider failure. Temperature and humidity are contextual model-grid weather fields, not air-quality sensor observations. The public API forecast is a clearly labeled untrained persistence baseline; offline Random Forest evaluation is not silently activated in production.

## Model validation

1. Prepare validated station/day PM2.5 data in µg/m³.
2. Aggregate to the target series without looking at future timestamps.
3. Sort chronologically; train on the first 80%, score on the final 20%.
4. Report MAE and RMSE for both prior-day persistence and Random Forest.
5. Keep the sample benchmark and output model **out** of operational alert decisions.

## CI and release gates

```mermaid
flowchart LR
    A[GitHub push / pull request] --> B[pytest]
    A --> C[Python compileall]
    A --> D[React npm build]
    B --> E{Checks pass?}
    C --> E
    D --> E
    E -->|Yes| F[Ready for manual review]
    E -->|No| G[Fix and retry]
```

A green CI result does not certify provider connectivity, accessibility, geographic representativeness, ML generalization, production security, or a deployment. No automatic cloud deployment is configured by this repository.
