"""Validated configuration; demonstration and real-data modes never mix silently."""
import os
from dotenv import load_dotenv
load_dotenv()
from dataclasses import dataclass

CITIES = {
    "Hyderabad": (17.3850, 78.4867),
    "Delhi": (28.6139, 77.2090),
    "Mumbai": (19.0760, 72.8777),
    "Bengaluru": (12.9716, 77.5946),
    "Chennai": (13.0827, 80.2707),
}


@dataclass(frozen=True)
class Settings:
    mode: str = "demo"
    key: str = ""
    db_path: str = "data/processed/airaware.db"


def settings() -> Settings:
    mode = os.getenv("AIR_DATA_MODE", "demo").strip().lower()
    if mode not in ("demo", "live"):
        raise ValueError("AIR_DATA_MODE must be 'demo' or 'live'")
    return Settings(mode, os.getenv("OPENAQ_API_KEY", ""), os.getenv("DATABASE_PATH", "data/processed/airaware.db"))
