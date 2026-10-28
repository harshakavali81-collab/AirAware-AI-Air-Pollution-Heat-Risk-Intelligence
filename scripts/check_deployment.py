"""Verify an *already deployed* AirAware HTTPS service without exposing credentials.

This is a deployment/observation freshness smoke gate, not a measurement
calibration or a scientific model validation. Must not fabricate live readiness.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import ipaddress
import json
from urllib.parse import urlparse

import httpx


def _external_host(host: str) -> bool:
    """Reject localhost and non-global IPs in externally dispatched CI smoke tests."""
    host = host.lower().rstrip('.')
    if host in ('localhost',) or host.endswith(('.localhost', '.local', '.internal')):
        return False
    try:
        return ipaddress.ip_address(host).is_global
    except ValueError:
        return '.' in host


def _valid_reading(value: object, now: datetime, max_age_minutes: int):
    if not isinstance(value, dict):
        return None
    if value.get('units') not in ('µg/m³', 'µg/m3', 'ug/m3'):
        return None
    if not value.get('station') or value.get('source') != 'OpenAQ v3 latest':
        return None
    pm25 = value.get('pm25')
    if isinstance(pm25, bool) or not isinstance(pm25, (int, float)) or not 0 <= pm25 <= 2000:
        return None
    timestamp = value.get('measured_at_utc')
    if not isinstance(timestamp, str):
        return None
    try:
        measured = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    except ValueError:
        return None
    if measured.tzinfo is None:
        return None
    age_minutes = (now - measured.astimezone(timezone.utc)).total_seconds() / 60
    if not -15 <= age_minutes <= max_age_minutes:
        return None
    return value['station'], age_minutes


def check_remote(
    url: str,
    *,
    require_live: bool = False,
    client: httpx.Client | None = None,
    max_age_minutes: int = 2880,
    min_stations: int = 1,
) -> dict:
    parsed = urlparse(url)
    if (parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password
            or not _external_host(parsed.hostname) or parsed.port not in (None, 443)):
        raise ValueError('Provide a public HTTPS hostname without credentials or custom port')
    if parsed.query or parsed.fragment or parsed.path not in ('', '/'):
        raise ValueError('Provide the site HTTPS origin, without path, query or fragment')
    if not 1 <= max_age_minutes <= 10080 or not 1 <= min_stations <= 50:
        raise ValueError('Invalid measurement age or station-coverage threshold')

    base = url.rstrip('/')
    session = client or httpx.Client(timeout=20, follow_redirects=False)
    checks = {}
    try:
        for name, path in (('health', '/api/health'), ('ready', '/api/ready'), ('homepage', '/')):
            response = session.get(base + path)
            checks[name] = {'status': response.status_code, 'ok': response.is_success}
            if name != 'homepage':
                try:
                    payload = response.json()
                except ValueError:
                    payload = {}
                checks[name]['mode'] = payload.get('mode')
                checks[name]['status_field'] = payload.get('status')
                expected = 'ok' if name == 'health' else 'ready'
                checks[name]['ok'] &= payload.get('status') == expected
            else:
                checks[name]['html_found'] = '<html' in response.text.lower()
                checks[name]['ok'] &= checks[name]['html_found']
        if require_live:
            response = session.get(base + '/api/latest', params={'city': 'Hyderabad'})
            try:
                data = response.json()
            except ValueError:
                data = {}
            readings = data.get('readings') if isinstance(data, dict) else None
            readings = readings if isinstance(readings, list) else []
            now = datetime.now(timezone.utc)
            valid = [_valid_reading(v, now, max_age_minutes) for v in readings]
            valid = [v for v in valid if v is not None]
            reporting_stations = len({station for station, _ in valid})
            checks['latest'] = {
                'status': response.status_code,
                'mode': data.get('mode') if isinstance(data, dict) else None,
                'readings_total': len(readings),
                'fresh_valid_readings': len(valid),
                'fresh_reporting_stations': reporting_stations,
                'freshness_limit_minutes': max_age_minutes,
                'ok': response.is_success and data.get('mode') == 'live'
                and reporting_stations >= min_stations
                and all(checks[c]['mode'] == 'live' for c in ('health', 'ready')),
                'caveat': 'Fresh sensor timestamps do not prove calibration, citywide coverage or forecast validity.',
            }
    finally:
        if client is None:
            session.close()
    return {
        'url': base,
        'pass': all(c['ok'] for c in checks.values()),
        'scope': 'HTTPS service availability and optional recent OpenAQ observations only; not forecast validation',
        'checks': checks,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', required=True, help='Existing public HTTPS origin of deployed full-stack service')
    parser.add_argument('--require-live', action='store_true')
    parser.add_argument('--max-reading-age-minutes', type=int, default=2880,
                        help='Maximum age for a latest PM2.5 observation, default 48 hours')
    parser.add_argument('--min-stations', type=int, default=1,
                        help='Minimum distinct stations with fresh valid PM2.5 readings')
    args = parser.parse_args()
    result = check_remote(args.url, require_live=args.require_live,
                          max_age_minutes=args.max_reading_age_minutes, min_stations=args.min_stations)
    print(json.dumps(result, indent=2))
    if not result['pass']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
