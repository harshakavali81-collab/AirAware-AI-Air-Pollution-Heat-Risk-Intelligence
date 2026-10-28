import pandas as pd


def anomalies(frame, window=14, threshold=3.0):
    """Exploratory rolling z-scores, not validated air pollution alerts."""
    if frame.empty:
        return []
    daily = frame.groupby("date", as_index=False).pm25.mean().sort_values("date")
    hist = daily.pm25.shift(1)
    avg = hist.rolling(window, min_periods=7).mean()
    std = hist.rolling(window, min_periods=7).std().replace(0, float("nan"))
    score = (daily.pm25 - avg) / std
    return [{"date": str(d), "pm25": round(float(v), 1), "z_score": round(float(z), 2)}
            for d, v, z in zip(daily.date, daily.pm25, score) if pd.notna(z) and abs(z) >= threshold]
