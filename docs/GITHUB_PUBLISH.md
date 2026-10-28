# Publish AirAware AI to GitHub (repository setup)

The AirAware-AI repository does not exist on the connected GitHub account at the time this project archive was assembled. The case study is already committed to `harshakavali81-collab/harshavardhan-portfolio`, but the entire application source has already been pushed under [`harshavardhan-portfolio/projects/AirAware-AI`](https://github.com/harshakavali81-collab/harshavardhan-portfolio/tree/main/projects/AirAware-AI). The instructions below are only for optionally creating a **separate standalone** repository.

## Step 1 — Create the empty repository

Visit https://github.com/new while logged in to the account `harshakavali81-collab`.

- Repository name: `AirAware-AI`
- Description: `Air pollution and heat intelligence dashboard — OpenAQ v3, FastAPI, React, ML and data quality`
- Visibility: public, if you want recruiters to read the source
- Do **not** auto-add a README or .gitignore; this archive already includes them.

## Step 2 — Push the source from your machine

In a terminal opened inside the extracted `AirAware-AI` folder:

```bash
git init
git branch -M main
git add .
git commit -m "Initial AirAware AI full-stack educational application"
git remote add origin https://github.com/harshakavali81-collab/AirAware-AI.git
git push -u origin main
```

Authenticate using your own GitHub login or Git Credential Manager. Do not paste a personal access token into ChatGPT. If `origin` already exists, inspect `git remote -v` before changing anything. Do not force-push an existing repository.

## Step 3 — Verify

1. Visit https://github.com/harshakavali81-collab/AirAware-AI to confirm the files appear.
2. Check the **Actions** tab for the Python tests and frontend build. The npm build was not independently checked in the offline development environment.
3. Confirm the README images render. Add the case-study URL to the repository About field.
4. Once a successful source push is verified, update `harshavardhan-portfolio/airaware.html` and the homepage card to point to the real source.
5. Set `OPENAQ_API_KEY` only as a backend environment secret, never committed to GitHub.

## Optional Vercel frontend

Import the new GitHub repository into Vercel; set Root Directory to `frontend`, Build Command to `npm run build`, and Output Directory to `dist`. Set `VITE_API_BASE` to a verified HTTPS backend origin. A static Vercel deployment without a working backend will not have data.
