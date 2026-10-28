"""Build an example synthetic CSV, SQL snapshot and optional visual report."""
from pathlib import Path
import pandas as pd
from src.airaware.ingestion.demo import demo_readings
from src.airaware.processing.features import daily_city_average
from backend.app.db.store import save_frame

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data'/'processed'
OUT.mkdir(parents=True,exist_ok=True)
df=demo_readings('Hyderabad',120)
df.to_csv(OUT/'hyderabad_synthetic_pm25.csv',index=False)
save_frame(OUT/'airaware.db','Hyderabad',df)
print('Created synthetic CSV and SQLite examples in data/processed')
