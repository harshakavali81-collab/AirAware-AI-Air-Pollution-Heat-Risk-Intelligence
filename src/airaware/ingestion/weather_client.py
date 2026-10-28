"""Open-Meteo weather retrieval, separate from measured OpenAQ station air quality."""
import httpx


def current_weather(lat: float, lon: float, client: httpx.Client | None = None):
    http = client or httpx.Client(timeout=12)
    response = http.get("https://api.open-meteo.com/v1/forecast", params={
        "latitude": lat, "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature",
        "timezone": "UTC", "forecast_days": 1,
    })
    response.raise_for_status()
    body = response.json()
    value = body.get("current", {})
    return {
        "temperature_c": value.get("temperature_2m"),
        "humidity_pct": value.get("relative_humidity_2m"),
        "apparent_temperature_c": value.get("apparent_temperature"),
        "observed_at": value.get("time"),
        "source": "Open-Meteo forecast/model grid (not a station observation)",
    }
