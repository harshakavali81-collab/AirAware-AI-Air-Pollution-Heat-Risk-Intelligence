"""Reproducible historical PM2.5 benchmark using UCI's Beijing observations.

Not an OpenAQ ingestion test, current India forecast, or clinical validation.
Data credited to Song Xi Chen, UCI dataset 501, CC BY 4.0.
https://doi.org/10.24432/C5RK5G
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from zipfile import ZipFile, BadZipFile

import pandas as pd

from src.airaware.models.rolling_backtest import rolling_origin_evaluation

UCI_DATASET = "https://archive.ics.uci.edu/dataset/501/beijing+multi+site+air+quality+data"
UCI_ZIP = "https://archive.ics.uci.edu/static/public/501/beijing+multi+site+air+quality+data.zip"
UCI_DOI = "https://doi.org/10.24432/C5RK5G"
MAX_DOWNLOAD_BYTES = 25_000_000


def download_official_archive() -> bytes:
    """Only downloads the canonical UCI archive; no arbitrary user URL accepted."""
    req = Request(UCI_ZIP, headers={"User-Agent": "AirAware-AI-Research-Benchmark/1.0"})
    with urlopen(req, timeout=65) as response:
        data = response.read(MAX_DOWNLOAD_BYTES + 1)
    if len(data) > MAX_DOWNLOAD_BYTES:
        raise ValueError("Dataset download exceeds 25MB safety limit")
    if not data.startswith(b"PK"):
        raise ValueError("Dataset download was not a ZIP archive")
    return data


def _iter_csv_bytes(archive: bytes):
    """UCI may pack CSV files in a ZIP nested inside another ZIP."""
    with ZipFile(io.BytesIO(archive)) as outer:
        for info in outer.infolist():
            if info.is_dir() or info.file_size > 15_000_000:
                continue
            name = Path(info.filename).name.lower()
            if name.startswith("prsa_data_") and name.endswith(".csv"):
                yield info.filename, outer.read(info)
            elif name.startswith("prsa2017_") and name.endswith(".zip"):
                inner_data = outer.read(info)
                with ZipFile(io.BytesIO(inner_data)) as inner:
                    for item in inner.infolist():
                        if item.is_dir() or item.file_size > 15_000_000:
                            continue
                        if Path(item.filename).name.lower().startswith("prsa_data_") and item.filename.lower().endswith(".csv"):
                            yield item.filename, inner.read(item)


def import_beijing(archive: bytes) -> tuple[pd.DataFrame, dict]:
    """Convert hourly station rows to daily observed station means; no imputation.

    Date is the Beijing local *calendar day*, encoded at UTC midnight only to
    satisfy the existing calendar-evaluation interface, not an instant of measurement.
    """
    rows = []
    station_files = 0
    source_hourly = 0
    missing_pm25 = 0
    try:
        entries = list(_iter_csv_bytes(archive))
    except (BadZipFile, OSError) as exc:
        raise ValueError("Invalid Beijing archive") from exc
    if not entries:
        raise ValueError("No PRSA_Data_*.csv station files found in archive")
    for filename, csv_bytes in entries:
        hourly = pd.read_csv(io.BytesIO(csv_bytes))
        need = {"year", "month", "day", "hour", "PM2.5", "station"}
        if not need.issubset(hourly.columns):
            raise ValueError(f"Unexpected station file schema: {filename}")
        station_files += 1
        source_hourly += len(hourly)
        missing_pm25 += int(hourly["PM2.5"].isna().sum())
        pm = pd.to_numeric(hourly["PM2.5"], errors="coerce")
        date = pd.to_datetime(hourly[["year", "month", "day"]], errors="coerce", utc=True)
        clean = pd.DataFrame({"date": date, "station": hourly["station"].astype(str), "pm25": pm})
        clean = clean.dropna(subset=["date", "station", "pm25"])
        clean = clean[clean.pm25.between(0, 2000)]
        rows.append(clean.groupby(["date", "station"], as_index=False)["pm25"].mean())
    combined = pd.concat(rows, ignore_index=True)
    # Duplicate station-day rows should not be double-weighted in city mean.
    combined = combined.groupby(["date", "station"], as_index=False)["pm25"].mean()
    combined["source"] = "UCI Beijing monitoring-site historical observations (2013-2017)"
    return combined.sort_values(["date", "station"]), {
        "source_hourly_rows": source_hourly,
        "source_missing_pm25_rows": missing_pm25,
        "station_csv_files": station_files,
        "daily_station_rows": int(len(combined)),
        "stations": int(combined.station.nunique()),
        "first_date": combined.date.min().date().isoformat(),
        "last_date": combined.date.max().date().isoformat(),
    }


def evaluate_archive(archive: bytes, *, origin: str, horizon_days: int = 60, min_train_rows: int = 850) -> dict:
    daily, details = import_beijing(archive)
    result = rolling_origin_evaluation(
        daily, city="Beijing (historical 2013–2017)", min_observed_days=365,
        min_train_rows=min_train_rows, horizon_days=horizon_days,
        min_coverage_pct=90,
    )
    # These are verified as UCI data only if downloaded directly from UCI by this script.
    result.update({
        "source_kind": "real_historical_observations" if origin == "direct_official_uci_download" else "unverified_local_archive",
        "data_classification": "public_historical_beijing_not_current_india",
        "input": details,
        "dataset": {"name": "Beijing Multi-Site Air Quality", "repository": UCI_DATASET,
                    "doi": UCI_DOI, "license": "CC BY 4.0", "period": "2013-03-01/2017-02-28",
                    "location": "Beijing, China", "time_base": "Beijing local calendar days",
                    "daily_aggregation": "arithmetic mean of available station hourly readings; then equal-weight station daily means",
                    "provenance": origin},
        "archive_sha256": hashlib.sha256(archive).hexdigest(),
        "publication_notes": [
            "Historical measurement benchmark only; it does not validate a live Hyderabad or OpenAQ feed.",
            "Out-of-time forecasting test on 2013-2017 Beijing; station instrumentation and coverage must be reviewed.",
            "No training on future dates, but one-day-ahead scoring does use the previous observed day inside each evaluation window.",
            "Data © original contributors, redistributed by UCI under CC BY 4.0, DOI 10.24432/C5RK5G.",
        ],
    })
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a historical real-observation benchmark")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--download-official", action="store_true", help="Fetch directly from UCI data repository")
    source.add_argument("--archive", type=Path, help="Local archive (unverified, for offline reproductions)")
    parser.add_argument("--output", type=Path, default=Path("reports/uci_beijing_historical.json"))
    args = parser.parse_args()
    blob = download_official_archive() if args.download_official else args.archive.read_bytes()
    report = evaluate_archive(blob, origin="direct_official_uci_download" if args.download_official else "user_supplied_local_archive")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "data_kind": report["source_kind"], "stations": report["input"]["stations"], "folds": report["fold_count"], "MAE_ug_m3": report["mean_fold_mae"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
