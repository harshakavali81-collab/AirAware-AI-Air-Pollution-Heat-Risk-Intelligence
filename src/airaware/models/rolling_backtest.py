"""Conservative, reproducible, rolling-origin backtest for station PM2.5 data.

This module never certifies a forecast, infers air quality index categories, or
identifies a data file as trusted measurements solely because it has a filename.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

from src.airaware.processing.features import FEATURES, daily_city_average, make_features
from src.airaware.processing.validation import validate_measurements


def _error_summary(actual: np.ndarray, pred: np.ndarray) -> dict:
    delta = np.asarray(actual, dtype=float) - np.asarray(pred, dtype=float)
    return {"mae": round(float(np.mean(np.abs(delta))), 4),
            "rmse": round(float(np.sqrt(np.mean(delta ** 2))), 4)}


def rolling_origin_evaluation(frame: pd.DataFrame, *, city: str, allow_synthetic: bool = False,
                              min_observed_days: int = 90, min_train_rows: int = 60,
                              horizon_days: int = 14, min_coverage_pct: float = 80.0) -> dict:
    """Score one-day-ahead predictions on successive disjoint calendar windows.

    All predictors are prior-day observations. Each fold trains strictly before
    its test window and is evaluated against the same persistence benchmark.
    This is statistical backtesting, NOT external scientific validation.
    """
    if not 1 <= horizon_days <= 60:
        raise ValueError("horizon_days must be between 1 and 60")
    if not 0 < min_coverage_pct <= 100:
        raise ValueError("min_coverage_pct must be in (0, 100]")
    if not {"date", "station", "pm25"}.issubset(frame.columns):
        raise ValueError("Input must include date, station, pm25")
    if frame.empty:
        raise ValueError("No observations supplied")
    if not allow_synthetic and "source" in frame.columns:
        if frame["source"].astype(str).str.contains("synthetic|demo|fabricat", case=False, regex=True).any():
            raise ValueError("Synthetic rows rejected; pass allow_synthetic=True only for explicit demonstrations")

    clean = validate_measurements(frame)
    if clean.empty:
        raise ValueError("No valid measurements after cleaning")
    daily = daily_city_average(clean).sort_values("date")
    observed_days = len(daily)
    if observed_days < min_observed_days:
        raise ValueError(f"Too few observed days: {observed_days}; require {min_observed_days}")
    # Calendar regularization prevents a lag-1 feature from actually spanning
    # several missing days (a common error in source-data backtests).
    start, end = daily.date.min(), daily.date.max()
    calendar_days = (end - start).days + 1
    coverage_pct = round(100 * observed_days / calendar_days, 2)
    if coverage_pct < min_coverage_pct:
        raise ValueError(f"Calendar coverage {coverage_pct}% below gate {min_coverage_pct}%")
    regular = daily.set_index("date").asfreq("D").rename_axis("date").reset_index()
    features = make_features(regular)
    if len(features) < min_train_rows + horizon_days * 3:
        raise ValueError("Too few fully lagged rows for three non-overlapping evaluation windows")

    folds = []
    # Expanding training set, most recent contiguous non-overlapping windows.
    # Test-row dates can contain gaps due to missing lagged features; all folds
    # remain disjoint and train strictly on earlier calendar dates.
    window = horizon_days
    boundary = min_train_rows
    while boundary + window <= len(features):
        train = features.iloc[:boundary]
        test = features.iloc[boundary:boundary + window]
        model = RandomForestRegressor(n_estimators=80, max_depth=7,
                                      min_samples_leaf=3, random_state=42, n_jobs=1)
        model.fit(train[FEATURES], train.pm25)
        rf = np.maximum(0.0, model.predict(test[FEATURES]))
        persistence = test.lag1.to_numpy(dtype=float)
        fold = {
            "train_end": pd.Timestamp(train.date.iloc[-1]).date().isoformat(),
            "test_start": pd.Timestamp(test.date.iloc[0]).date().isoformat(),
            "test_end": pd.Timestamp(test.date.iloc[-1]).date().isoformat(),
            "train_rows": len(train), "test_rows": len(test),
            "persistence": _error_summary(test.pm25.to_numpy(), persistence),
            "random_forest": _error_summary(test.pm25.to_numpy(), rf),
        }
        assert fold["train_end"] < fold["test_start"]
        folds.append(fold)
        boundary += window
    if len(folds) < 3:
        raise ValueError("At least three evaluation folds are required")
    model_mae = float(np.mean([f["random_forest"]["mae"] for f in folds]))
    baseline_mae = float(np.mean([f["persistence"]["mae"] for f in folds]))
    return {
        "city": city, "evaluated_at_utc": datetime.now(timezone.utc).isoformat(),
        "evaluation_kind": "rolling_origin_one_day_ahead_exploratory",
        "verification": "offline_statistical_backtest_not_independently_validated",
        "data_classification": "synthetic_permitted_for_demo" if allow_synthetic else "user_provided_not_source_verified",
        "measurement_units": "µg/m³", "observed_days": observed_days,
        "calendar_days": calendar_days, "calendar_coverage_pct": coverage_pct,
        "stations_in_input": int(clean.station.nunique()),
        "folds": folds, "fold_count": len(folds),
        "mean_fold_mae": {"persistence": round(baseline_mae, 4), "random_forest": round(model_mae, 4)},
        "candidate_beats_baseline_in_folds": sum(f["random_forest"]["mae"] < f["persistence"]["mae"] for f in folds),
        "caveats": [
            "This is not a regulatory, medical, or emergency warning product.",
            "Station representativeness, sensors, licensing and timestamps require independent verification.",
            "Overlapping station coverage, geography and seasonal drift can affect scores.",
            "A model should not be deployed without independently reviewed out-of-period validation.",
        ],
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Conservative real-data backtest; never certifies real-world accuracy")
    ap.add_argument("--csv", required=True, help="CSV with date,station,pm25 and optional source column")
    ap.add_argument("--city", default="Hyderabad")
    ap.add_argument("--output", default="data/processed/rolling_backtest_report.json")
    ap.add_argument("--allow-synthetic", action="store_true", help="Only for clearly labeled synthetic demos")
    args = ap.parse_args()
    report = rolling_origin_evaluation(pd.read_csv(args.csv), city=args.city, allow_synthetic=args.allow_synthetic)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(out), "verification": report["verification"],
                      "fold_count": report["fold_count"], "mean_fold_mae": report["mean_fold_mae"]}, indent=2))


if __name__ == "__main__":
    main()
