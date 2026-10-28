"""Post-deployment smoke verification; run against a URL you own. Never claims validation by itself."""
from __future__ import annotations
import argparse
import json
from urllib.parse import urlparse
import httpx


def check_remote(url: str, *, require_live: bool = False, client: httpx.Client | None = None) -> dict:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Provide a public https:// hostname without embedded credentials")
    if parsed.query or parsed.fragment or parsed.path not in ("", "/"):
        raise ValueError("Provide the site's HTTPS origin, without path, query or fragment")
    base = url.rstrip("/")
    session = client or httpx.Client(timeout=20, follow_redirects=True)
    checks = {}
    try:
        for name, path in (("health", "/api/health"), ("ready", "/api/ready"), ("homepage", "/")):
            response = session.get(base + path)
            checks[name] = {"status": response.status_code, "ok": response.is_success}
            if name != "homepage":
                payload = response.json()
                checks[name]["mode"] = payload.get("mode")
                checks[name]["status_field"] = payload.get("status")
            else:
                checks[name]["html_found"] = "<html" in response.text.lower()
                checks[name]["ok"] = checks[name]["ok"] and checks[name]["html_found"]
        if require_live:
            response = session.get(base + "/api/latest", params={"city": "Hyderabad"})
            data = response.json()
            readings = data.get("readings") if isinstance(data, dict) else []
            checks["latest"] = {
                "status": response.status_code,
                "mode": data.get("mode") if isinstance(data, dict) else None,
                "readings_count": len(readings) if isinstance(readings, list) else 0,
                "ok": response.is_success and data.get("mode") == "live" and isinstance(readings, list) and len(readings) > 0,
                "caveat": "Provider data may be stale or geographically incomplete; check measurement timestamps",
            }
    finally:
        if client is None:
            session.close()
    ok = all(c["ok"] for c in checks.values())
    return {"url": base, "pass": ok, "scope": "HTTP and optional upstream ingestion only; not forecast skill or production certification", "checks": checks}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True, help="Existing HTTPS origin for deployed service")
    ap.add_argument("--require-live", action="store_true", help="Require nonempty authenticated source readings")
    args = ap.parse_args()
    result = check_remote(args.url, require_live=args.require_live)
    print(json.dumps(result, indent=2))
    if not result["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
