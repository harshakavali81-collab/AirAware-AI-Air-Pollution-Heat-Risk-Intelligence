"""Source-level tests for independent public deployment HTTP gates."""
import httpx
import pytest
from scripts.verify_public_urls import check_static_demo

def _client(body='<!doctype html><html><body>AIRAWARE SYNTHETIC preview</body></html>', status=200):
    return httpx.Client(transport=httpx.MockTransport(
        lambda request: httpx.Response(status_code=status, text=body)))

def test_static_demo_accepts_good_page():
    with _client() as c:
        v = check_static_demo("https://demo.example.org/", client=c)
    assert v["pass"] and v["synthetic_disclosure"]

@pytest.mark.parametrize("body", [
    "<html>AIRAWARE live observed data</html>",
    "<html>SYNTHETIC unrelated company</html>",
    "AIRAWARE SYNTHETIC plain text",
])
def test_static_demo_rejects_missing_evidence(body):
    with _client(body) as c:
        assert not check_static_demo("https://demo.example.org/", client=c)["pass"]

def test_static_demo_fails_http_error():
    with _client(status=404) as c:
        assert not check_static_demo("https://demo.example.org/", client=c)["pass"]

@pytest.mark.parametrize("url", [
    "http://demo.example.org/",
    "https://localhost/",
    "https://127.0.0.1/",
    "https://name:password@demo.example.org/",
    "https://demo.example.org:8443/",
    "https://demo.example.org/#fragment",
])
def test_static_demo_rejects_unsafe_urls(url):
    with pytest.raises(ValueError):
        check_static_demo(url)
