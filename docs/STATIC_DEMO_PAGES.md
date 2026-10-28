# Publish the standalone browser preview with GitHub Pages

A dedicated `gh-pages` branch has been created at source commit `6e6dfeb960020186a6a5538b87766d830fec0c4a`. Its root contains **only** `index.html`, `README.md` and `.nojekyll`.

## Enable Pages (repo owner, once)

1. Open [Settings → Pages](https://github.com/harshakavali81-collab/AirAware-AI-Air-Pollution-Heat-Risk-Intelligence/settings/pages).
2. Set **Build and deployment → Source** to **Deploy from a branch**.
3. Select **gh-pages** and **/(root)**. Click **Save**.
4. Review **Actions → pages build and deployment** and confirm its conclusion is `success`.
5. After verified publication, check the **expected** Pages URL: `https://harshakavali81-collab.github.io/AirAware-AI-Air-Pollution-Heat-Risk-Intelligence/` and verify the page displays the synthetic-demo disclosure.

The expected URL is a path template, not a verified active site until the owner enables Pages and checks HTTP responses.

## Critical scope separation

| Surface | Git branch/hosting | Demonstrates | Does NOT demonstrate |
|---|---|---|---|
| Static interactive preview | `gh-pages` (requires Pages enabling) | Synthetic city trends, cards, and interactivity | Real OpenAQ readings, Python API, deployed model, operational forecasts |
| Portfolio case study | `harshavardhan-portfolio` | Source links and historical benchmark | Public FastAPI service |
| Full-stack API + React | `main` + `render.yaml` (requires owner activation) | When deployed and checked, backend and frontend | Real-data scientific validity by hosting alone |
| Actual live sensor data | OpenAQ key held in hosting secrets, `AIR_DATA_MODE=live` | Timestamped readings where covered | Calibrated citywide forecasts |
| Power BI | `powerbi/AirAwareReport/AirAware.pbip` | Editable structured source | Microsoft Desktop-verified PBIX |

## Before promising completion

- Verify GitHub CI on `main`.
- For the **full-stack site**, use `python -m scripts.check_deployment --url https://YOUR_ACTUAL_PUBLIC_HOST`.
- For real OpenAQ readings, use the stricter `--require-live --min-stations 1 --max-reading-age-minutes 2880` and inspect timestamps, station identity and geographic coverage.
- Document real forecast performance with representative Indian measurements; Beijing historical benchmark alone does not establish India forecast skill.
- Open and validate the report in genuine Power BI Desktop and export PBIX if required.

This preview is an independently publishable portfolio demonstration, **not** the externally hosted live application.
