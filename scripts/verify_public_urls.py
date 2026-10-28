"""Independent public URL verification; a static demo is not a live monitoring service."""
from __future__ import annotations
import argparse
import json
from urllib.parse import urlparse
import httpx
from scripts.check_deployment import check_remote, _external_host

def check_static_demo(url: str, *, client: httpx.Client | None = None) -> dict:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or not _external_host(parsed.hostname):
        raise ValueError("Static demo must use a public HTTPS hostname")
    if parsed.username or parsed.password or parsed.port not in (None, 443):
        raise ValueError("Credentials and custom ports are not permitted")
    if parsed.query or parsed.fragment:
        raise ValueError("Do not supply query or fragment")
    session = client or httpx.Client(timeout=25, follow_redirects=True)
    try:
        response = session.get(url)
        page = response.text.lower() if response.is_success else ""
        result = {
            "url": url, "http_status": response.status_code,
            "has_html": "<html" in page,
            "has_airaware_brand": "airaware" in page or "air aware" in page,
            "synthetic_disclosure": "synthetic" in page,
        }
        result["pass"] = bool(response.is_success and result["has_html"]
                              and result["has_airaware_brand"] and result["synthetic_disclosure"])
        result["scope"] = "Public static synthetic-only HTML preview; no API/real sensor validation"
        return result
    finally:
        if client is None:
            session.close()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo-url", required=True)
    parser.add_argument("--fullstack-url", default="")
    parser.add_argument("--require-live", action="store_true")
    parser.add_argument("--max-reading-age-minutes", type=int, default=2880)
    parser.add_argument("--min-stations", type=int, default=1)
    args = parser.parse_args()
    result = {"static_demo": check_static_demo(args.demo_url)}
    if args.fullstack_url:
        result["fullstack_service"] = check_remote(
            args.fullstack_url, require_live=args.require_live,
            max_age_minutes=args.max_reading_age_minutes, min_stations=args.min_stations)
    else:
        result["fullstack_service"] = {
            "pass": None,
            "status": "not configured — set repository Actions variable AIRAWARE_FULLSTACK_URL",
        }
    print(json.dumps(result, indent=2))
    if not result["static_demo"]["pass"] or result["fullstack_service"].get("pass") is False:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
