"""Train time-ordered baseline vs RandomForest; never report synthetic scores as real efficacy."""
import argparse
import json
from pathlib import Path
import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from src.airaware.config import CITIES
from src.airaware.ingestion.demo import demo_readings
from src.airaware.processing.features import daily_city_average, make_features, FEATURES
from src.airaware.processing.validation import validate_measurements
import pandas as pd


def metrics(y, prediction):
    return {"mae": round(float(mean_absolute_error(y, prediction)), 3),
            "rmse": round(float(np.sqrt(mean_squared_error(y, prediction))), 3)}


def train_and_evaluate(city="Hyderabad", output=None, frame=None):
    source = "synthetic_demo"
    if frame is not None:
        from_source = "source" in frame.columns and frame["source"].astype(str).str.contains("Synthetic", case=False).all()
        source = "synthetic_demo_csv" if from_source else "provided_csv_unverified"
    daily = daily_city_average(validate_measurements(frame) if frame is not None else demo_readings(city, 180))
    feature_rows = make_features(daily)
    if len(feature_rows) < 30:
        raise ValueError("Need at least 30 complete feature rows")
    split = int(len(feature_rows) * 0.8)
    train, test = feature_rows.iloc[:split], feature_rows.iloc[split:]
    model = RandomForestRegressor(n_estimators=120, max_depth=7, min_samples_leaf=3, random_state=42, n_jobs=1)
    model.fit(train[FEATURES], train.pm25)
    rf_pred = np.maximum(0, model.predict(test[FEATURES]))
    baseline_pred = test.lag1.to_numpy()
    report = {"city": city, "data_mode": source, "evaluation": "chronological 80/20 holdout, one-day predictions", "train_rows": len(train),
              "test_rows": len(test), "baseline": metrics(test.pm25, baseline_pred),
              "random_forest": metrics(test.pm25, rf_pred), "model_selected": "random_forest" if mean_absolute_error(test.pm25, rf_pred) < mean_absolute_error(test.pm25, baseline_pred) else "last_value_baseline"}
    if output:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"model": model, "city": city, "metrics": report, "features": FEATURES}, path)
        path.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--city", choices=list(CITIES), default="Hyderabad")
    parser.add_argument("--output", default="data/processed/demo_model.joblib")
    parser.add_argument("--csv", help="Optional real or exported CSV with date, station and pm25 columns; requires at least 30 feature rows")
    args = parser.parse_args()
    frame = pd.read_csv(args.csv) if args.csv else None
    print(json.dumps(train_and_evaluate(args.city, args.output, frame=frame), indent=2))
