# One-container full-stack deployment: Vite production frontend + FastAPI API.
FROM node:22-alpine AS frontend-build
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY backend ./backend
RUN pip install --no-cache-dir . && useradd --create-home --uid 10001 airaware
COPY --from=frontend-build /frontend/dist /app/frontend/dist
RUN mkdir -p /app/data/processed && chown -R airaware:airaware /app/data
USER airaware
ENV AIR_DATA_MODE=demo PYTHONUNBUFFERED=1 PORT=8000
EXPOSE 8000
CMD ["sh", "-c", "exec uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
