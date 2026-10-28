# Source tree and module responsibilities

![Project tree](../assets/project-tree.png)

```text
AirAware-AI/
├── .github/workflows/ci.yml        Python tests and React build checks
├── .env.example                    Demo/live configuration and safe API-key placeholder
├── README.md                       Project overview, quick start and safety notice
├── backend/
│   └── app/
│       ├── main.py                 FastAPI entrypoint and routes
│       ├── service.py              Read-only application service
│       ├── routes/                 Endpoint package
│       └── db/store.py             SQLite demo snapshots
├── src/airaware/
│   ├── ingestion/                  OpenAQ, Open-Meteo, demo adapters
│   ├── processing/                 Data cleaning, validation, feature engineering
│   ├── models/                     Baseline forecast, offline training and evaluation
│   └── monitoring/                 Freshness and anomaly signals
├── frontend/
│   ├── src/components/             Metric and chart components
│   ├── src/pages/                  Dashboard, StationMap, Forecast, Trends, Quality
│   ├── src/api/                    Browser-safe API client
│   ├── package.json
│   └── Dockerfile
├── notebooks/                      EDA, weather joining and forecast evaluation
├── scripts/                        Demo export, gallery and notebook creation
├── assets/                         Exactly 10 original PNG visuals
├── data/                           Synthetic CSV and documented data folders
├── docs/                           Model card, architecture, gallery, workflow, runbook
├── powerbi/                        CSV import / DAX guidance (no compiled PBIX)
├── tests/                          Unit/API tests, network mocked
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

Ignored by Git: `.env`, local SQLite database, cached Python files, `*.joblib` artifacts, local node modules, and built frontend output. Generate them locally when needed. Never commit API keys, private location traces or unlicensed data.
