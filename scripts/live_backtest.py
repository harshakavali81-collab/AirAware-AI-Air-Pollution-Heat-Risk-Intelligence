"""Retrieve actual OpenAQ data with owner's key and evaluate a chronological split.

No public measurements or live results are fabricated. Store license/provenance metadata.
"""
import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from src.airaware.config import CITIES
from src.airaware.ingestion.live import live_readings
from src.airaware.models.train import train_and_evaluate
from src.airaware.processing.validation import validate_measurements


def run(city, days, output, key):
    if city not in CITIES:
        raise ValueError(f"Unsupported city {city}")
    if not key:
        raise ValueError("Set OPENAQ_API_KEY securely before performing live backtests")
    df, locations = live_readings(city, key, days)
    df = validate_measurements(df)
    if df.empty:
        raise ValueError("No valid PM2.5 observations were returned: check coverage and sensor units")
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    meta = {
        "mode": "live_provider_export", "provider": "OpenAQ API v3",
        "source_url": "https://docs.openaq.org/api", "city": city,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "requested_days": days, "observed_rows": len(df),
        "earliest_date": str(df.date.min()), "latest_date": str(df.date.max()),
        "reporting_stations": int(df.station.nunique()),
        "discovered_pm25_sensors": len(locations),
        "units": "µg/m³", "license": "verify each provider's applicable terms",
        "caveat": "Daily station averages, not real-time AQI; coverage incomplete."
    }
    # Metadata records a real ingestion event but not validation against a reference standard.
    try:
        report = train_and_evaluate(city, frame=df)
        meta["backtest"] = report
        meta["backtest_status"] = "evaluated_unverified_real_world_skill"
    except ValueError as error:
        meta["backtest_status"] = "insufficient_data"
        meta["backtest_reason"] = str(error)
    out.with_suffix('.metadata.json').write_text(json.dumps(meta, indent=2), encoding='utf-8')
    return meta


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument('--city', choices=sorted(CITIES), default='Hyderabad')
    parser.add_argument('--days', type=int, choices=range(30, 366), metavar='30..365', default=120)
    parser.add_argument('--output', default='data/processed/live_openaq_pm25.csv')
    args = parser.parse_args()
    print(json.dumps(run(args.city, args.days, args.output, os.getenv('OPENAQ_API_KEY', '')), indent=2))
