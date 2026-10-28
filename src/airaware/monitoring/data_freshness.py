from datetime import datetime, timezone
import pandas as pd


def freshness(frame):
    if frame.empty:
        return {"latest_date": None, "age_days": None, "status": "no_data"}
    latest = pd.to_datetime(frame.date, utc=True).max().to_pydatetime()
    age = max(0, (datetime.now(timezone.utc) - latest).total_seconds() / 86400)
    return {"latest_date": latest.isoformat(), "age_days": round(age, 1),
            "status": "stale" if age > 3 else "recent"}
