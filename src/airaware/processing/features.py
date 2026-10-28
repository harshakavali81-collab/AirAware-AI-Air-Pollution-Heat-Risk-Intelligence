"""Lagged features built without using a future target to predict the past."""
import pandas as pd

FEATURES = ["lag1", "lag7", "rolling7", "dow"]


def daily_city_average(frame: pd.DataFrame):
    if frame.empty:
        return pd.DataFrame(columns=["date", "pm25"])
    clean = frame.copy()
    clean["date"] = pd.to_datetime(clean["date"], utc=True)
    return clean.groupby("date", as_index=False)["pm25"].mean().sort_values("date")


def make_features(frame: pd.DataFrame):
    result = frame.copy().sort_values("date")
    result["lag1"] = result.pm25.shift(1)
    result["lag7"] = result.pm25.shift(7)
    result["rolling7"] = result.pm25.shift(1).rolling(7).mean()
    result["dow"] = pd.to_datetime(result.date).dt.dayofweek
    return result.dropna(subset=FEATURES + ["pm25"]).reset_index(drop=True)


def join_weather(pm: pd.DataFrame, weather: pd.DataFrame):
    """Explicit UTC daily date join: missing weather stays missing, never fabricated."""
    a, b = pm.copy(), weather.copy()
    a["date"] = pd.to_datetime(a.date, utc=True).dt.date
    b["date"] = pd.to_datetime(b.date, utc=True).dt.date
    return a.merge(b, on="date", how="left", validate="many_to_one")
