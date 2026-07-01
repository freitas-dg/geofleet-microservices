from typing import Protocol, List
from domain.entities import DriverLocation

class SearchRepository(Protocol):
    async def find_nearby(self, lat: float, lng: float, radius_km: float, limit: int = 50) -> List[dict]:
        ...
