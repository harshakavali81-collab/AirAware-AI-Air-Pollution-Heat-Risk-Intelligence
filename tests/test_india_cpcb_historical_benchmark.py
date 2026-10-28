"""Offline tests with invented fixture; never report them as real India results."""
import io
import pandas as pd
import pytest
from scripts.india_cpcb_historical_benchmark import import_station_days, evaluate_csv


def fake_csv(days=366):
    d = pd.date_range("2024-01-01", periods=days, freq="D")
    frame = pd.DataFrame([{"station_id": "site_1", "parameter_name": "PM2.5",
                           "unit": "µg/m³", "period_start": dt.date().isoformat(),
                           "mean": float(45 + (i % 13))}
                          for i, dt in enumerate(d)])
    return frame.to_csv(index=False).encode()


def test_hyderabad_example_parses_correct_units_and_days():
    d, meta = import_station_days(fake_csv())
    assert len(d) == 366
    assert meta["days_with_observations"] == 366
    assert meta["stations"] == 1
    assert d["pm25"].min() >= 0


def test_fixture_not_marked_verified_and_backtests():
    r = evaluate_csv(fake_csv(), origin="unverified_local_csv")
    assert r["source_kind"] == "local_unverified_csv"
    assert r["data_classification"] == "historical_2024_hyderabad_observation_not_current_openaq"
    assert r["fold_count"] >= 3
    assert "random_forest" in r["mean_fold_mae"]


@pytest.mark.parametrize("name,value", [
    ("unit", "ppb"), ("parameter_name", "PM10"), ("period_start", "2025-01-01"),
    ("station_id", ""), ("mean", "unavailable"),
])
def test_untrusted_rows_rejected(name, value):
    df = pd.read_csv(io.BytesIO(fake_csv()))
    df[name] = value
    with pytest.raises(ValueError):
        import_station_days(df.to_csv(index=False).encode())


def test_invalid_schema_fails():
    with pytest.raises(ValueError, match="schema"):
        import_station_days(b"date,value\n2024-01-01,5\n")


def test_duplicate_station_day_deduplicated():
    df = pd.read_csv(io.BytesIO(fake_csv()))
    df = pd.concat([df, df.iloc[[0]]], ignore_index=True)
    parsed, meta = import_station_days(df.to_csv(index=False).encode())
    assert len(parsed) == 366
    assert meta["duplicate_station_dates_deduplicated"] == 1
