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


def test_openaq_daily_paginates_for_long_histories():
    seen = []
    def handler(req):
        page = int(req.url.params['page'])
        seen.append(page)
        n = 100 if page == 1 else 17
        return httpx.Response(200, json={'results':[{'value':page}] * n})
    c = OpenAQClient('fake-test-key', httpx.Client(transport=httpx.MockTransport(handler)))
    assert len(c.daily(88, 150)) == 117
    assert seen == [1,2]


def test_latest_mocked_sensor_timestamp_and_key(monkeypatch):
    from src.airaware.ingestion.live import live_latest
    def handler(req):
        assert req.headers['X-API-Key'] == 'test'
        if req.url.path == '/v3/locations':
            return httpx.Response(200,json={'results':[{'id':42,'name':'Mock PM2.5 station','sensors':[{'id':4,'parameter':{'name':'pm25','units':'µg/m³'}}]}]})
        if req.url.path == '/v3/locations/42/latest':
            return httpx.Response(200,json={'results':[{'sensorsId':4,'value':12.4,'datetime':{'utc':'2026-10-28T04:00:00Z'}}, {'sensorsId':999,'value':80,'datetime':{'utc':'2026-10-28T04:00:00Z'}}]})
        return httpx.Response(404)
    http=httpx.Client(transport=httpx.MockTransport(handler))
    monkeypatch.setattr('src.airaware.ingestion.live.OpenAQClient',lambda key: OpenAQClient(key,http))
    rows=live_latest('Hyderabad','test')
    assert len(rows)==1 and rows[0]['pm25']==12.4 and rows[0]['source']=='OpenAQ v3 latest'
