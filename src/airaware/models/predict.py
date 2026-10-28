"""Transparent recursive forecast; strictly separate forecast from measured observations."""
from datetime import timedelta
import pandas as pd
from src.airaware.processing.features import daily_city_average


def forecast(frame, horizon=7):
    if not 1 <= horizon <= 14:
        raise ValueError("horizon must be 1-14 days")
    history = daily_city_average(frame)
    if history.empty:
        return []
    last = pd.to_datetime(history.date.max()).date()
    # This is an untrained persistence baseline, not a weather-informed prediction.
    last_value = round(float(history.pm25.iloc[-1]), 1)
    return [{"date": (last + timedelta(days=n)).isoformat(), "pm25": last_value,
             "kind": "forecast", "method": "last_observed_day_persistence_baseline",
             "units": "µg/m³"} for n in range(1, horizon + 1)]
