"""Data validation and completeness metrics; no fake confidence score."""
import pandas as pd


def validate_measurements(frame: pd.DataFrame):
    required = {"date", "station", "pm25"}
    if not required.issubset(frame.columns):
        raise ValueError("Missing required columns: " + ", ".join(sorted(required - set(frame.columns))))
    clean = frame.copy()
    clean["date"] = pd.to_datetime(clean["date"], errors="coerce", utc=True)
    clean["pm25"] = pd.to_numeric(clean["pm25"], errors="coerce")
    clean = clean.dropna(subset=["date", "station", "pm25"])
    clean = clean.loc[clean.pm25.ge(0) & clean.pm25.le(2000)]
    return clean.drop_duplicates(subset=["date", "station"], keep="last").sort_values(["date", "station"])


def coverage(frame, days):
    if frame.empty:
        return {"observed_station_days": 0, "expected_station_days": 0, "coverage_pct": 0, "missing_pct": 100}
    stations = frame.station.nunique()
    expected = stations * days
    actual = len(frame)
    pct = min(100, 100 * actual / max(expected, 1))
    return {"observed_station_days": actual, "expected_station_days": expected,
            "coverage_pct": round(pct, 1), "missing_pct": round(100 - pct, 1)}
