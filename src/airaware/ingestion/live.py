"""Live station ingestion: PM2.5 only; respects unit metadata and source coverage."""
import pandas as pd
from src.airaware.config import CITIES
from src.airaware.ingestion.openaq_client import OpenAQClient
from src.airaware.processing.clean import normalize_openaq_days


def live_readings(city: str, key: str, days: int = 90):
    lat, lon = CITIES[city]
    client = OpenAQClient(key)
    locations = client.locations(lat, lon)
    output, meta = [], []
    for location in locations:
        for sensor in location.get("sensors", []):
            parameter = sensor.get("parameter", {})
            if parameter.get("name", "").lower() not in ("pm25", "pm2.5"):
                continue
            units = parameter.get("units", "")
            if units not in ("µg/m³", "µg/m3", "ug/m3"):
                continue
            sid = sensor["id"]
            station_id = str(location["id"])
            output.extend(normalize_openaq_days(client.daily(sid, days), station_id, sid, units))
            meta.append({"id": station_id, "name": location.get("name", station_id),
                         "latitude": (location.get("coordinates") or {}).get("latitude"),
                         "longitude": (location.get("coordinates") or {}).get("longitude"),
                         "source": "OpenAQ v3", "provider": (location.get("provider") or {}).get("name")})
    columns = ["date", "station", "sensor", "pm25", "parameter", "source", "units"]
    return pd.DataFrame(output, columns=columns), meta


def live_latest(city: str, key: str, max_locations: int = 8):
    """Latest *reported* PM2.5 readings, not a guaranteed real-time feed.

    OpenAQ latest is a last timestamp in each sensor's series, not a complete
    ingestion log. Never replace unavailable values with synthetic readings.
    """
    from datetime import datetime, timezone
    from src.airaware.ingestion.openaq_client import AirDataError
    lat, lon = CITIES[city]
    client = OpenAQClient(key)
    places = client.locations(lat, lon, limit=max_locations)
    records = []
    now = datetime.now(timezone.utc)
    for loc in places[:max_locations]:
        allowed = set()
        for sensor in loc.get("sensors", []):
            param = sensor.get("parameter") or {}
            if param.get("name", "").lower() in ("pm25", "pm2.5") and param.get("units", "") in ("µg/m³", "µg/m3", "ug/m3"):
                allowed.add(sensor.get("id"))
        if not allowed:
            continue
        for rec in client.latest(loc['id']):
            if rec.get('sensorsId') not in allowed:
                continue
            measured = (rec.get('datetime') or {}).get('utc')
            value = rec.get('value')
            if measured is None or not isinstance(value, (int, float)) or not (0 <= value <= 2000):
                continue
            try:
                dt = datetime.fromisoformat(measured.replace('Z','+00:00')).astimezone(timezone.utc)
                age = max(0, int((now-dt).total_seconds()/60))
            except (ValueError, TypeError):
                continue
            records.append({'station':str(loc['id']), 'station_name':loc.get('name'),
                            'sensor_id':rec['sensorsId'], 'pm25':float(value),
                            'measured_at_utc':dt.isoformat(), 'age_minutes':age,
                            'units':'µg/m³', 'source':'OpenAQ v3 latest'})
    return sorted(records, key=lambda r:r['measured_at_utc'], reverse=True)
