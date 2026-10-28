import json
from pathlib import Path
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from scripts.live_backtest import run


def test_health_without_credentials_and_api_access():
    with TestClient(app) as c:
        assert c.get('/api/health').status_code == 200
        assert c.get('/api/cities').json()['cities']


def test_live_backtest_without_key_fails_fast(tmp_path):
    with pytest.raises(ValueError, match='OPENAQ_API_KEY'):
        run('Hyderabad', 90, tmp_path/'out.csv', '')


def test_live_backtest_never_claims_success_without_rows(tmp_path, monkeypatch):
    import scripts.live_backtest as m
    monkeypatch.setattr(m,'live_readings',lambda city,key,days:(pd.DataFrame(columns=['date','station','pm25']),[]))
    with pytest.raises(ValueError, match='No valid'):
        run('Hyderabad', 90, tmp_path/'out.csv','fake-in-test')


def test_deployment_specs_are_explicit():
    root = Path(__file__).resolve().parents[1]
    assert (root/'render.yaml').exists()
    d = (root/'Dockerfile').read_text()
    assert 'frontend-build' in d and 'PORT' in d
    assert 'OPENAQ_API_KEY' not in (root/'render.yaml').read_text().replace('OPENAQ_API_KEY','')
