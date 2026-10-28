import httpx
import pytest
from scripts.check_deployment import check_remote


def test_remote_check_rejects_bad_urls():
    for url in ["http://example.org", "https://name:secret@example.org", "https://example.org/evil", "localhost:8000"]:
        with pytest.raises(ValueError):
            check_remote(url)


def test_remote_checks_demo_without_claiming_live():
    def handler(request):
        if request.url.path == "/api/health":
            return httpx.Response(200, json={"status": "ok", "mode": "demo"})
        if request.url.path == "/api/ready":
            return httpx.Response(200, json={"status": "ready", "mode": "demo"})
        if request.url.path == "/api/latest":
            return httpx.Response(200, json={"mode": "demo", "readings": []})
        return httpx.Response(200, text="<!doctype html><html><body>ok</body></html>")
    c = httpx.Client(transport=httpx.MockTransport(handler))
    assert check_remote("https://demo.example.org", client=c)["pass"]
    r = check_remote("https://demo.example.org", require_live=True, client=c)
    assert not r["pass"] and not r["checks"]["latest"]["ok"]
    c.close()
