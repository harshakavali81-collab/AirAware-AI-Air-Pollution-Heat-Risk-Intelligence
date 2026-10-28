"""Normalize sensor readings with explicit units and timezone-aware dates."""
from datetime import datetime, timezone
import math
import pandas as pd


def normalize_openaq_days(rows, station, sensor, units="µg/m³"):
    if units not in ("µg/m³", "µg/m3", "ug/m3"):
        return []  # Never silently combine incompatible units.
    cleaned = []
    for entry in rows:
        period = entry.get("period", {}) or {}
        dt = (period.get("datetimeFrom", {}) or {}).get("utc") or entry.get("datetime", {}).get("utc")
        value = entry.get("value")
        if not dt or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            continue
        try:
            stamp = pd.to_datetime(dt, utc=True).date().isoformat()
        except (TypeError, ValueError):
            continue
        cleaned.append({"date": stamp, "station": str(station), "sensor": str(sensor),
                        "parameter": "pm25", "pm25": round(float(value), 2), "source": "OpenAQ v3", "units": "µg/m³"})
    return cleaned


def utc_now():
    return datetime.now(timezone.utc).isoformat()
