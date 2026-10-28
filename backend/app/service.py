"""Functional API service, with explicit provenance and availability behavior."""
from functools import lru_cache
import time
import pandas as pd
from src.airaware.config import CITIES, settings
from src.airaware.ingestion.demo import demo_readings, demo_weather
from src.airaware.ingestion.live import live_readings
from src.airaware.ingestion.weather_client import current_weather
from src.airaware.processing.validation import validate_measurements, coverage
from src.airaware.processing.features import daily_city_average
from src.airaware.monitoring.data_freshness import freshness
from src.airaware.monitoring.anomalies import anomalies
from src.airaware.models.predict import forecast


def heat_band(apparent):
    """Illustrative perceived-heat band; NOT an official warning or medical risk prediction."""
    if apparent is None:
        return "unavailable"
    return "very high" if apparent >= 40 else "high" if apparent >= 32 else "elevated" if apparent >= 27 else "lower"


@lru_cache(maxsize=8)
def live_cache(city, key, bucket):
    return live_readings(city, key, 120)


def snapshot(city):
    if city not in CITIES:
        raise ValueError("Unsupported city")
    config = settings()
    lat, lon = CITIES[city]
    if config.mode == "demo":
        frame = demo_readings(city)
        stations = [{"id": f"DEMO-{city[:3].upper()}-{i+1}",
                     "name": f"Synthetic point {i+1}", "latitude": round(lat + (i - 1) * 0.038, 4),
                     "longitude": round(lon + (i - 1) * 0.029, 4),
                     "source": "Synthetic demonstration data"} for i in range(3)]
        weather = demo_weather(city)
    else:
        frame, stations = live_cache(city, config.key, int(time.time() // 600))
        try:
            weather = current_weather(lat, lon)
        except Exception:
            weather = {"temperature_c": None, "humidity_pct": None, "apparent_temperature_c": None,
                       "observed_at": None, "source": "Open-Meteo temporarily unavailable"}
    frame = validate_measurements(frame)
    # Validation does not imply all underlying sensors meet regulatory standards.
    return {"city": city, "lat": lat, "lon": lon, "mode": config.mode, "frame": frame,
            "stations": stations, "weather": weather,
            "notice": "DEMO — generated synthetic readings; not real air quality or weather." if config.mode == "demo" else
                      "OpenAQ source readings; station coverage and latest dates vary. No real-time guarantee."}


def overview(s):
    frame = s["frame"]
    city_daily = daily_city_average(frame)
    current = float(city_daily.pm25.iloc[-1]) if not city_daily.empty else None
    previous = float(city_daily.pm25.iloc[-2]) if len(city_daily) >= 2 else None
    return {"city": s["city"], "mode": s["mode"], "notice": s["notice"],
            "latitude": s["lat"], "longitude": s["lon"], "units": "µg/m³", "parameter": "PM2.5",
            "latest_daily_mean": round(current, 1) if current is not None else None,
            "day_change_pct": round((current-previous)/previous*100, 1) if current is not None and previous else None,
            "station_count": frame.station.nunique() if not frame.empty else 0,
            "weather": {**s["weather"], "illustrative_heat_band": heat_band(s["weather"].get("apparent_temperature_c"))},
            "freshness": freshness(frame), "quality": coverage(frame, 120)}


def station_summary(s):
    frame = s["frame"]
    result = []
    for station in s["stations"]:
        data = frame.loc[frame.station == station["id"]].sort_values("date")
        result.append({**station, "pm25": round(float(data.pm25.iloc[-1]), 1) if not data.empty else None,
                       "last_day": data.date.iloc[-1].date().isoformat() if not data.empty else None,
                       "units": "µg/m³", "measurement_type": "daily aggregate"})
    return result


def trends(s, days):
    frame = s["frame"]
    daily = daily_city_average(frame).tail(days)
    return [{"date": row.date.date().isoformat(), "pm25": round(float(row.pm25), 2),
             "kind": "synthetic" if s["mode"] == "demo" else "daily_observed_aggregate"}
            for row in daily.itertuples(index=False)]


def quality(s):
    frame = s["frame"]
    return {"coverage": coverage(frame, 120), "freshness": freshness(frame),
            "exploratory_anomalies": anomalies(frame), "caveat": "Missing coverage is based on discovered stations and a 120-day window, not all possible monitoring sites."}


def forecast_data(s, days):
    return {"city": s["city"], "mode": s["mode"], "forecast": forecast(s["frame"], days),
            "method": "last-observed-day persistence (untrained baseline)",
            "caveat": "Illustrative extrapolation, not a certified AQ forecast. Future dates are not measured values."}
