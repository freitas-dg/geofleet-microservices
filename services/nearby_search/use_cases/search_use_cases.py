from typing import List
from domain.entities import DriverLocation
from domain.repositories import SearchRepository

class SearchNearbyUseCase:
    def __init__(self, repository: SearchRepository):
        self.repository = repository

    async def execute(self, lat: float, lng: float, radius_km: float) -> List[DriverLocation]:
        if radius_km <= 0 or radius_km > 50:
            raise ValueError("Radius must be between 0 and 50 km")
        return await self.repository.find_nearby(lat, lng, radius_km)
