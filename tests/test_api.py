import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def demo(monkeypatch):
    monkeypatch.setenv("AIR_DATA_MODE", "demo")


def test_health():
    r=client.get('/api/health')
    assert r.status_code == 200 and r.json()['mode']=='demo'


def test_cities():
    assert 'Hyderabad' in client.get('/api/cities').json()['cities']


def test_overview_labeled_demo():
    data=client.get('/api/overview').json()
    assert data['mode']=='demo' and 'synthetic' in data['notice'].lower()
    assert data['units']=='µg/m³' and data['station_count']==3


def test_trends_capped():
    d=client.get('/api/trends?days=7').json()
    assert d['mode']=='demo' and len(d['trends'])==7


def test_invalid_days():
    assert client.get('/api/trends?days=999').status_code == 422
    assert client.get('/api/forecast?days=0').status_code == 422


def test_invalid_city():
    assert client.get('/api/overview?city=Atlantis').status_code == 422


def test_stations_are_synthetic():
    rows=client.get('/api/stations').json()['stations']
    assert len(rows)==3 and all('Synthetic' in r['name'] for r in rows)


def test_forecast_labeled():
    d=client.get('/api/forecast').json()
    assert len(d['forecast'])==7
    assert all(x['kind']=='forecast' for x in d['forecast'])
    assert 'untrained' in d['method']


def test_quality():
    d=client.get('/api/quality').json()
    assert d['coverage']['coverage_pct'] < 100
    assert 0 <= d['coverage']['missing_pct'] <= 100


def test_live_mode_no_key(monkeypatch):
    monkeypatch.setenv('AIR_DATA_MODE','live')
    monkeypatch.delenv('OPENAQ_API_KEY', raising=False)
    r=client.get('/api/overview')
    assert r.status_code == 503 and 'OPENAQ_API_KEY' in r.json()['detail']
