# GitHub source publishing and release notes

**Current dedicated source repository:** https://github.com/harshakavali81-collab/AirAware-AI-Air-Pollution-Heat-Risk-Intelligence

The application, 10 original PNG images, documentation, automated workflow, source notebooks and tests are committed to the **`main`** branch. The repository's GitHub Actions checks verify the Python test job and frontend build on GitHub.

**Portfolio case study:** https://harshakavali81-collab.github.io/harshavardhan-portfolio/airaware.html

## Clone and run

```bash
git clone https://github.com/harshakavali81-collab/AirAware-AI-Air-Pollution-Heat-Risk-Intelligence.git
cd AirAware-AI-Air-Pollution-Heat-Risk-Intelligence
python -m pip install -e '.[dev]'
python -m pytest -q
uvicorn backend.app.main:app --reload
```

In a second terminal, `cd frontend && npm install && npm run dev`.

## Updates and pull requests

```bash
git checkout -b docs/your-improvement
# edit files, test locally
python -m pytest -q
git add .
git commit -m "Document AirAware improvements"
git push -u origin docs/your-improvement
```

Then open a pull request against `main`. Never force-push the published main branch. See `CONTRIBUTING.md` and `docs/WORKFLOW.md`.

## What the public repository does not prove

The CI build verifies code checks only. It does not mean the React/FastAPI app is deployed publicly, that OpenAQ connectivity was successfully authenticated, that real sensor coverage is sufficient, or that a model has been validated on measured pollution data. Set `OPENAQ_API_KEY` only on the backend or as a deployment secret. See `docs/OPERATIONS.md` for production readiness tasks.
