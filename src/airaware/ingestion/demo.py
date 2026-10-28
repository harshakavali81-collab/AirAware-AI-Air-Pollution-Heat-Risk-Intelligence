"""Reproducible SYNTHETIC readings. Names are hypothetical, not actual monitoring stations."""
from datetime import datetime, timezone, timedelta
import numpy as np
import pandas as pd
from src.airaware.config import CITIES


def demo_readings(city: str, days: int = 120) -> pd.DataFrame:
    if city not in CITIES:
        raise ValueError("Unknown city")
    seed = sum(ord(c) for c in city) + 2026
    rng = np.random.default_rng(seed)
    start = datetime.now(timezone.utc).date() - timedelta(days=days)
    base = {"Hyderabad": 27, "Delhi": 64, "Mumbai": 30, "Bengaluru": 22, "Chennai": 25}[city]
    results = []
    for i in range(days):
        date = (start + timedelta(days=i)).isoformat()
        seasonal = 8 * np.cos(2 * np.pi * i / 45)
        for station in range(3):
            # Introduce repeatable gaps to exercise quality reporting.
            if (i * 7 + station * 11 + seed) % 37 == 0:
                continue
            level = max(2.0, base + seasonal + station * 5 + 4 * np.sin(i / 6) + rng.normal(0, 5))
            results.append({"date": date, "station": f"DEMO-{city[:3].upper()}-{station+1}",
                            "sensor": f"synthetic-{station+1}", "pm25": round(float(level), 2),
                            "parameter": "pm25", "source": "Synthetic demonstration data", "units": "µg/m³"})
    return pd.DataFrame(results)


def demo_weather(city: str):
    return {"temperature_c": 31.2, "humidity_pct": 56, "apparent_temperature_c": 35.1,
            "observed_at": datetime.now(timezone.utc).isoformat(),
            "source": "Synthetic demonstration weather — not observed or forecast"}
