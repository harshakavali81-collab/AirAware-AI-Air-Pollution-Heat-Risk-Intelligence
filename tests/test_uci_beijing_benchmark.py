"""Test historical benchmark import without pretending our fixtures are real data."""
import io
from zipfile import ZipFile

import pandas as pd
import pytest

from scripts.uci_beijing_benchmark import import_beijing, evaluate_archive


def nested_archive():
    dates = pd.date_range("2013-03-01", periods=1000, freq="D")
    rows = []
    for day in dates:
        for hour in (6, 12, 18, 23):
            rows.append({"No": len(rows)+1, "year":day.year, "month":day.month,
                         "day":day.day, "hour":hour,
                         "PM2.5": float(40 + (len(rows) % 19)), "station":"Aotizhongxin"})
    out = io.BytesIO()
    inner = io.BytesIO()
    with ZipFile(inner, "w") as z:
        z.writestr("PRSA_Data_Aotizhongxin_20130301-20170228.csv", pd.DataFrame(rows).to_csv(index=False))
    with ZipFile(out, "w") as z:
        z.writestr("PRSA2017_Data_20130301-20170228.zip", inner.getvalue())
    return out.getvalue()


def test_uci_nested_zip_station_day_aggregation():
    df, meta = import_beijing(nested_archive())
    assert meta["stations"] == 1
    assert meta["daily_station_rows"] == 1000
    assert meta["source_hourly_rows"] == 4000
    assert set(["station", "date", "pm25", "source"]).issubset(df.columns)


def test_uci_local_fixture_never_claims_verified_source():
    result = evaluate_archive(nested_archive(), origin="user_supplied_local_archive", min_train_rows=500)
    assert result["source_kind"] == "unverified_local_archive"
    assert len(result["archive_sha256"]) == 64
    assert result["fold_count"] >= 3


def test_uci_rejects_unrecognized_or_broken_archives():
    buf = io.BytesIO()
    with ZipFile(buf, "w") as z:
        z.writestr("example.txt", "not data")
    with pytest.raises(ValueError, match="No PRSA_Data_"):
        import_beijing(buf.getvalue())
    with pytest.raises(ValueError, match="Invalid Beijing archive"):
        import_beijing(b"fakezip")
