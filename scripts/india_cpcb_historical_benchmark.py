"""Historical Hyderabad PM2.5 evaluation from licensed Indian monitoring data.

Public India Air Quality Database by XKDR Forum; CPCB CAAQM source, CC BY 4.0.
https://airquality.xkdr.org/  (public *demo* key only accesses 2024 data)

This is not authenticated OpenAQ, an active Indian deployment, a real-time
monitor, or an independently validated operational forecast.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd

from src.airaware.models.rolling_backtest import rolling_origin_evaluation

API_ROOT = "https://airquality.xkdr.org/v1/measurements"
SOURCE = "https://github.com/xKDR/Air-Quality-Database"
PUBLIC_DEMO_KEY = "aqi_demo_wbf92Qx21zX-Wa_Tg8Dx1nXe"  # Published as public example by XKDR
YEAR = 2024
MAX_CSV_BYTES = 5_000_000
ALLOWED_UNITS = {"µg/m³", "µg/m3", "μg/m³", "ug/m3", "ug/m^3", "µg/m^3"}


def download_hyderabad_2024() -> tuple[bytes, dict]:
    """Query the documented XKDR endpoint, limiting to 2024 and one pollutant.

    Uses provider-published demo credentials, not a user secret. Not suitable
    for unrestricted traffic or real-time operation.
    """
    params = {"city": "Hyderabad", "parameter": "PM2.5", "start": "2024-01-01",
              "end": "2024-12-31", "agg": "daily", "format": "csv"}
    req = Request(API_ROOT + "?" + urlencode(params), headers={
        "Authorization": "Bearer " + PUBLIC_DEMO_KEY,
        "User-Agent": "AirAware-AI-Historical-Research/1.0",
        "Accept": "text/csv",
    })
    with urlopen(req, timeout=55) as response:
        if response.status != 200:
            raise ValueError(f"Historical provider returned HTTP {response.status}")
        if str(response.headers.get("X-Truncated", "false")).lower() in ("true", "1", "yes"):
            raise ValueError("Historical provider response was truncated")
        payload = response.read(MAX_CSV_BYTES + 1)
        headers = {"row_count_header": response.headers.get("X-Row-Count"),
                   "truncated_header": response.headers.get("X-Truncated")}
    if len(payload) > MAX_CSV_BYTES:
        raise ValueError("Historical CSV exceeded size limit")
    return payload, headers


def import_station_days(csv_bytes: bytes) -> tuple[pd.DataFrame, dict]:
    """Parse provider daily aggregate; local-day label is not a UTC event time."""
    if not csv_bytes or len(csv_bytes) > MAX_CSV_BYTES:
        raise ValueError("Empty or oversized CSV")
    table = pd.read_csv(io.BytesIO(csv_bytes))
    required = {"station_id", "parameter_name", "unit", "period_start", "mean"}
    if not required.issubset(table.columns):
        raise ValueError(f"Historical CSV schema missing {sorted(required - set(table.columns))}")
    if table.empty:
        raise ValueError("No monitoring observations returned")
    # Fail the entire import rather than silently discarding unexpected pollutants/units.
    if not table["parameter_name"].astype(str).eq("PM2.5").all():
        raise ValueError("Unexpected pollutant in PM2.5 request")
    if not table["unit"].astype(str).isin(ALLOWED_UNITS).all():
        raise ValueError("Unexpected PM2.5 unit; do not infer conversions")
    station = table["station_id"].astype("string").str.strip()
    if station.isna().any() or station.eq("").any():
        raise ValueError("Missing station IDs")
    # Period_start is a local date or a timestamp labeled in IST by the provider.
    # We deliberately use only its calendar-day part, not timezone conversion.
    days = table["period_start"].astype(str).str[:10]
    dates = pd.to_datetime(days, errors="coerce", format="%Y-%m-%d", utc=True)
    if dates.isna().any() or not dates.dt.year.eq(YEAR).all():
        raise ValueError("Invalid calendar day or date outside requested 2024 window")
    vals = pd.to_numeric(table["mean"], errors="coerce")
    if vals.isna().any():
        raise ValueError("Non-numeric provider daily mean")
    raw_count = len(table)
    frame = pd.DataFrame({"date": dates, "station": station.astype(str), "pm25": vals,
                          "source": "XKDR India historical CPCB station PM2.5 2024"})
    frame = frame[frame.pm25.between(0, 2000)].copy()
    if len(frame) < raw_count * 0.8:
        raise ValueError("Excessive invalid PM2.5 readings in historical source")
    dupes = int(frame.duplicated(["date", "station"]).sum())
    # Duplicate station/day must not count twice; treat duplicates as data-quality caveat.
    frame = frame.groupby(["date", "station", "source"], as_index=False)["pm25"].mean()
    if frame.empty:
        raise ValueError("No valid daily station observations")
    return frame, {
        "provider_daily_rows": raw_count,
        "valid_daily_station_rows": len(frame),
        "duplicate_station_dates_deduplicated": dupes,
        "stations": int(frame.station.nunique()),
        "first_date": frame.date.min().date().isoformat(),
        "last_date": frame.date.max().date().isoformat(),
        "days_with_observations": int(frame.date.nunique()),
        "source_units": sorted(set(table.unit.astype(str))),
    }


def evaluate_csv(blob: bytes, *, origin: str = "unverified_fixture", download_headers: dict | None = None) -> dict:
    frame, meta = import_station_days(blob)
    # Do not pad missing monitoring days. A calendar-coverage gate is mandatory.
    result = rolling_origin_evaluation(frame, city="Hyderabad (historical monitoring, 2024)",
                                       min_observed_days=210, min_train_rows=120,
                                       horizon_days=30, min_coverage_pct=70)
    result.update({
        "source_kind": "xkdr_historical_cpcb_observations" if origin == "download_xkdr_api" else "local_unverified_csv",
        "data_classification": "historical_2024_hyderabad_observation_not_current_openaq",
        "source_csv_sha256": hashlib.sha256(blob).hexdigest(),
        "provider_headers": download_headers or {},
        "dataset": {
            "title": "India Air Quality Database (XKDR Forum), 2024 daily station-level CPCB PM2.5",
            "source": SOURCE, "api_reference": "https://airquality.xkdr.org/",
            "upstream": "Central Pollution Control Board (CPCB) CAAQM",
            "license": "CC BY 4.0 compilation, as described by XKDR; original source notices apply",
            "city": "Hyderabad", "country": "India", "period": "2024-01-01/2024-12-31",
            "parameter": "PM2.5", "units": "µg/m³", "aggregation": "station daily means as supplied by provider",
            "time_base": "Indian local calendar date; encoded as UTC midnight for calendar modeling only",
            "provenance": origin,
        },
        "input": meta,
        "caveats_india": [
            "This is historical CPCB monitoring data supplied by third-party XKDR, not direct OpenAQ authenticated access.",
            "A time-separated statistical comparison is not independently validated operational forecasting.",
            "Station distribution and sensor calibration are not independently verified.",
            "Citywide averages use available station-days and may change as reporting sites vary.",
            "For operational use independently verify calibration, geographic generalization, data provenance, drift and forecast horizon.",
        ],
    })
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Historical Hyderabad CPCB recorded-source backtest")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--download-xkdr-2024", action="store_true")
    src.add_argument("--csv", type=Path, help="Unverified local CSV fixture (never source-verified)")
    parser.add_argument("--output", type=Path, default=Path("reports/hyderabad_cpcb_historical_2024.json"))
    args = parser.parse_args()
    if args.download_xkdr_2024:
        blob, headers = download_hyderabad_2024()
        origin = "download_xkdr_api"
    else:
        blob, headers = args.csv.read_bytes(), {}
        origin = "unverified_local_csv"
    report = evaluate_csv(blob, origin=origin, download_headers=headers)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "source_kind": report["source_kind"],
                      "stations": report["input"]["stations"], "folds": report["fold_count"],
                      "mae_ug_m3": report["mean_fold_mae"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
