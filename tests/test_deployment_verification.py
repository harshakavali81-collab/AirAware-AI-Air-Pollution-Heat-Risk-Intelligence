from datetime import datetime, timedelta, timezone

import httpx
import pytest

from scripts.check_deployment import check_remote


def client(mode='demo', readings=None):
    def handler(request):
        if request.url.path == '/api/health':
            return httpx.Response(200, json={'status': 'ok', 'mode': mode})
        if request.url.path == '/api/ready':
            return httpx.Response(200, json={'status': 'ready', 'mode': mode})
        if request.url.path == '/api/latest':
            return httpx.Response(200, json={'mode': mode, 'readings': readings or []})
        return httpx.Response(200, text='<!doctype html><html><body>AirAware</body></html>')
    return httpx.Client(transport=httpx.MockTransport(handler))


def reading(*, age_hours=2, station='123', pm25=35, units='µg/m³'):
    dt = datetime.now(timezone.utc) - timedelta(hours=age_hours)
    return {'station': station, 'source': 'OpenAQ v3 latest', 'units': units, 'pm25': pm25,
            'measured_at_utc': dt.isoformat()}


@pytest.mark.parametrize('url', [
    'http://example.org', 'https://name:secret@example.org',
    'https://example.org/evil', 'localhost:8000', 'https://localhost',
    'https://127.0.0.1', 'https://10.0.0.12', 'https://example.org:8443',
    'https://example.org/?q=1', 'https://example.org/#x',
])
def test_remote_check_rejects_bad_urls(url):
    with pytest.raises(ValueError):
        check_remote(url)


def test_remote_checks_demo_without_claiming_live():
    with client() as c:
        assert check_remote('https://demo.example.org', client=c)['pass']
        result = check_remote('https://demo.example.org', require_live=True, client=c)
        assert not result['pass'] and not result['checks']['latest']['ok']


def test_live_requires_recent_real_provider_reading():
    with client('live', [reading()]) as c:
        result = check_remote('https://demo.example.org', require_live=True, client=c)
        assert result['pass']
        assert result['checks']['latest']['fresh_reporting_stations'] == 1


@pytest.mark.parametrize('values', [
    [reading(age_hours=72)],
    [reading(units='ppm')],
    [reading(station='')],
    [reading(pm25=-1)],
    [reading(age_hours=-2)],
])
def test_live_rejects_stale_unproven_or_invalid_readings(values):
    with client('live', values) as c:
        result = check_remote('https://demo.example.org', require_live=True, client=c)
        assert not result['pass']
        assert result['checks']['latest']['fresh_reporting_stations'] == 0


def test_live_requires_minimum_distinct_stations():
    with client('live', [reading(), reading(age_hours=3)]) as c:
        assert not check_remote('https://demo.example.org', require_live=True,
                                client=c, min_stations=2)['pass']
    with client('live', [reading(station='a'), reading(station='b')]) as c:
        assert check_remote('https://demo.example.org', require_live=True,
                            client=c, min_stations=2)['pass']


def test_thresholds_are_bounded():
    with pytest.raises(ValueError):
        check_remote('https://demo.example.org', max_age_minutes=0)
    with pytest.raises(ValueError):
        check_remote('https://demo.example.org', min_stations=51)
