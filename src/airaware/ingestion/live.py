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
