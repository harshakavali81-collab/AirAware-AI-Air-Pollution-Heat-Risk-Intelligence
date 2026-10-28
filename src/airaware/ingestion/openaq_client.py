"""OpenAQ v3 locations and per-sensor daily aggregates. Never exposes the API key."""
from datetime import date, timedelta
import httpx

API = "https://api.openaq.org/v3"


class AirDataError(Exception):
    pass


class OpenAQClient:
    def __init__(self, key: str, client: httpx.Client | None = None):
        if not key:
            raise AirDataError("OPENAQ_API_KEY is required for live mode; use AIR_DATA_MODE=demo otherwise")
        self.key = key
        self.client = client or httpx.Client(timeout=15, headers={"X-API-Key": key, "User-Agent": "AirAware-AI/1.0"})

    def get(self, path: str, **params):
        try:
            response = self.client.get(f"{API}{path}", params=params, headers={"X-API-Key": self.key})
            response.raise_for_status()
            return response.json().get("results", [])
        except (httpx.HTTPError, ValueError, KeyError) as exc:
            raise AirDataError("OpenAQ retrieval failed; check key, rate limits and coverage") from exc

    def locations(self, lat: float, lon: float, limit: int = 20):
        return self.get("/locations", coordinates=f"{lat:.4f},{lon:.4f}", radius=25000, limit=limit, page=1)

    def daily(self, sensor_id: int, days: int = 90):
        end = date.today()
        return self.get(f"/sensors/{sensor_id}/days", date_from=(end - timedelta(days=days)).isoformat(), date_to=end.isoformat(), limit=100, page=1)

    def latest(self, location_id: int):
        return self.get(f"/locations/{location_id}/latest")
