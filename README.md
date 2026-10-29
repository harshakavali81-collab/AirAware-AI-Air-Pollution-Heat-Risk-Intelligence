# 🌎 AirAware AI — Air Pollution & Heat Risk Intelligence

Explore source-labeled air-quality observations, weather, coverage and baseline forecasts through a Python API and React dashboard.

[Setup](#local-installation--setup-guide) · [Architecture](#architecture--system-design-diagram) · [Detailed guide](PROJECT_GUIDE.md) · [Repository standard](docs/REPOSITORY_STANDARD.md)

## Visuals

![Original illustrative AirAware dashboard with synthetic data](<assets/dashboard-preview.png>)

Existing project visual; diagrams and illustrative graphics are not evidence of a deployed application.

## Live Link / Demo

The isolated `gh-pages` branch provides an **interactive synthetic-data** dashboard at https://harshakavali81-collab.github.io/AirAware-AI-Air-Pollution-Heat-Risk-Intelligence/ . Its build and deployment workflow passed on October 28, 2026 (https://github.com/harshakavali81-collab/AirAware-AI-Air-Pollution-Heat-Risk-Intelligence/actions/runs/40658823721). GitHub Pages deployed successfully and an independent GitHub-hosted monitor confirmed HTTP 200, AirAware branding and synthetic-data disclosure ([successful monitor run](https://github.com/harshakavali81-collab/AirAware-AI-Air-Pollution-Heat-Risk-Intelligence/actions/runs/40661369257)). The full-stack backend URL is not configured.

**Not a live production backend:** This standalone preview needs no API key and contains fabricated educational sample data. Actual full-stack Render hosting, authenticated OpenAQ India sensor verification, real India forecasting performance and native Microsoft Power BI Desktop PBIX export remain owner-account-dependent. See https://github.com/harshakavali81-collab/AirAware-AI-Air-Pollution-Heat-Risk-Intelligence/issues/1 .

## Key Features

- Source and supporting materials indexed in [Repository standard](docs/REPOSITORY_STANDARD.md).
- Detailed methodology and project context in [Project guide](PROJECT_GUIDE.md).

## Tech Stack

![Python](https://img.shields.io/badge/Python-334155?style=flat-square) ![FastAPI](https://img.shields.io/badge/FastAPI-334155?style=flat-square) ![scikit-learn](https://img.shields.io/badge/scikit--learn-334155?style=flat-square) ![Pandas](https://img.shields.io/badge/Pandas-334155?style=flat-square) ![NumPy](https://img.shields.io/badge/NumPy-334155?style=flat-square) ![React](https://img.shields.io/badge/React-334155?style=flat-square) ![Docker](https://img.shields.io/badge/Docker-334155?style=flat-square)

Dependency versions and optional packages are defined in the repository manifests.

## Architecture / System Design Diagram

[Architecture documentation / diagram](<assets/system-architecture.png>)

## Local Installation & Setup Guide

```bash
git clone https://github.com/harshakavali81-collab/AirAware-AI-Air-Pollution-Heat-Risk-Intelligence.git
cd AirAware-AI-Air-Pollution-Heat-Risk-Intelligence
```

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate  |  macOS/Linux: source .venv/bin/activate
python -m pip install -e '.[dev]'
cp .env.example .env  # on Windows: copy .env.example .env
uvicorn backend.app.main:app --reload
```

Visit `http://localhost:8000/docs` (Swagger) or `http://localhost:8000/api/overview?city=Hyderabad`.

## Challenges & Solutions

**Repository organization:** this project uses `src/`, `backend/`, `frontend/`. Keeping those paths stable avoids breaking imports, asset links and deployment commands while the documentation follows a shared format. Project-specific technical limitations and prior release evidence are retained in [Project guide](PROJECT_GUIDE.md).

## Future Improvements

- Capture a reproducible end-to-end demo with runtime versions and sample inputs.
- Expand regression checks for invalid inputs and documented edge cases.
- Record measured results, data provenance and deployment limitations alongside each release.

## Scope and supporting evidence

> **A source-aware environmental intelligence dashboard.** See PM2.5 daily measurements, weather conditions, station coverage, trends, a transparent baseline forecast and data quality, with demo/live modes that never silently mix.

## Repository Structure

| Location | Purpose |
| --- | --- |
| `src/` | Source modules |
| `backend/` | Backend services |
| `frontend/` | Frontend interface |
| `tests/` | Tests |
| `docs/` | Documentation |
| `data/` | Data and samples |
| `powerbi/` | Power BI build assets |
| `assets/` | Visual assets |
| `scripts/` | Automation scripts |
| `.github/` | Issue forms, PR template and automated checks |

[Complete file inventory and workflow](docs/REPOSITORY_STANDARD.md). Runtime entry points retain their existing paths.

## Workflow & Tracking

Use the [bug and feature forms](https://github.com/harshakavali81-collab/AirAware-AI-Air-Pollution-Heat-Risk-Intelligence/issues/new/choose) to define work with acceptance criteria. Keep tasks in Todo → In progress → Review → Done, and link a pull request with `Closes #<number>`. See [the maintenance workflow](docs/REPOSITORY_STANDARD.md#workflow).

## License

Original project software is available under the [MIT License](LICENSE). See [licensing scope](docs/LICENSING.md) for third-party and data exclusions.

