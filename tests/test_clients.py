"""Offline contract tests. They do not validate provider uptime or credentials."""
import httpx
import pytest
from src.airaware.ingestion.openaq_client import OpenAQClient, AirDataError
from src.airaware.ingestion.weather_client import current_weather


def test_openaq_key_header_and_parse():
    def handler(req):
        assert req.headers.get('X-API-Key') == 'test-key'
        assert req.url.path == '/v3/locations'
        assert req.url.params['radius'] == '25000'
        return httpx.Response(200,json={'results':[{'id':42,'sensors':[]}]})
    http=httpx.Client(transport=httpx.MockTransport(handler))
    client=OpenAQClient('test-key', http)
    assert client.locations(17.385,78.4867)[0]['id']==42


def test_openaq_daily_route():
    def handler(req):
        assert req.url.path == '/v3/sensors/123/days'
        assert req.url.params.get('date_from')
        return httpx.Response(200,json={'results':[{'value':12.3}]})
    c=OpenAQClient('key',httpx.Client(transport=httpx.MockTransport(handler)))
    assert c.daily(123,30)[0]['value']==12.3


def test_no_key_is_explicit_error():
    with pytest.raises(AirDataError): OpenAQClient('')


def test_provider_rate_limit_is_explicit_error():
    c=OpenAQClient('key',httpx.Client(transport=httpx.MockTransport(lambda r:httpx.Response(429))))
    with pytest.raises(AirDataError): c.locations(1,1)


def test_openmeteo_current_fields():
    def handler(req):
        assert req.url.path == '/v1/forecast'
        return httpx.Response(200,json={'current':{'temperature_2m':30.5,'relative_humidity_2m':66,'apparent_temperature':35.6,'time':'2026-10-28T05:00'}})
    value=current_weather(17.385,78.4867,httpx.Client(transport=httpx.MockTransport(handler)))
    assert value['temperature_c']==30.5 and value['apparent_temperature_c']==35.6
    assert 'grid' in value['source']
