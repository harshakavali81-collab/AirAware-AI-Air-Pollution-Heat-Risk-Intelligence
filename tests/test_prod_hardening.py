"""Offline production guardrail tests; do not require or publish an API key."""
import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app import service
from src.airaware.models.rolling_backtest import rolling_origin_evaluation


def fixture_frame(count=160, source="Independently unverified CSV"):
    dates = pd.date_range("2026-01-01", periods=count, freq="D", tz="UTC")
    return pd.DataFrame({"date": dates, "station": ["A"] * count,
                         "pm25": 23 + 4*np.sin(np.arange(count)/8), "source": [source] * count})


def test_liveness_versus_readiness(monkeypatch):
    monkeypatch.setenv("AIR_DATA_MODE", "live")
    monkeypatch.delenv("OPENAQ_API_KEY", raising=False)
    c = TestClient(app)
    assert c.get("/api/health").status_code == 200
    resp = c.get("/api/ready")
    assert resp.status_code == 503 and resp.json()["reason"] == "openaq_key_not_configured"
    monkeypatch.setenv("OPENAQ_API_KEY", "test-not-real")
    assert c.get("/api/ready").status_code == 200
    assert "upstream" in c.get("/api/ready").json()["scope"]


def test_public_api_security_headers(monkeypatch):
    monkeypatch.setenv("AIR_DATA_MODE", "demo")
    resp = TestClient(app).get("/api/health")
    assert resp.headers["x-content-type-options"] == "nosniff"
    assert resp.headers["x-frame-options"] == "DENY"
    assert resp.headers["cache-control"] == "no-store"


def test_latest_cache_limits_provider_calls(monkeypatch):
    count = []
    service.cached_latest.cache_clear()
    monkeypatch.setattr(service, "live_latest", lambda city, key: count.append(city) or [{"sample": 1}])
    assert service.cached_latest("Hyderabad", "secret-only-in-memory", 100) == [{"sample": 1}]
    assert service.cached_latest("Hyderabad", "secret-only-in-memory", 100) == [{"sample": 1}]
    assert len(count) == 1
    service.cached_latest("Hyderabad", "secret-only-in-memory", 101)
    assert len(count) == 2
    service.cached_latest.cache_clear()


def test_rolling_backtest_uses_three_or_more_nonoverlapping_folds():
    out = rolling_origin_evaluation(fixture_frame(), city="Hyderabad")
    assert out["fold_count"] >= 3
    assert "not_independently_validated" in out["verification"]
    assert out["calendar_coverage_pct"] == 100
    assert all(f["train_end"] < f["test_start"] for f in out["folds"])
    assert all(out["folds"][i]["test_end"] < out["folds"][i+1]["test_start"] for i in range(len(out["folds"])-1))


def test_rolling_backtest_rejects_synthetic_unless_authorized():
    f = fixture_frame(source="Synthetic demo")
    with pytest.raises(ValueError, match="Synthetic rows rejected"):
        rolling_origin_evaluation(f, city="Hyderabad")
    d = rolling_origin_evaluation(f, city="Hyderabad", allow_synthetic=True)
    assert d["data_classification"] == "synthetic_permitted_for_demo"


def test_rolling_backtest_rejects_sparse_calendar():
    f = fixture_frame()
    f = f[f.date.dt.day % 3 == 1].copy()
    with pytest.raises(ValueError, match="Calendar coverage|Too few observed"):
        rolling_origin_evaluation(f, city="Hyderabad")


def test_rolling_backtest_does_not_accept_missing_columns():
    with pytest.raises(ValueError, match="date, station, pm25"):
        rolling_origin_evaluation(pd.DataFrame({"date": ["2026-01-01"]}), city="Hyderabad")
