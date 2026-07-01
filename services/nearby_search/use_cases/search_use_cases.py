from typing import List
from domain.entities import DriverLocation
from domain.repositories import SearchRepository

class SearchNearbyUseCase:
    def __init__(self, repository: SearchRepository):
        self.repository = repository

    async def execute(self, lat: float, lng: float, radius_km: float, limit: int = 50) -> List[dict]:
        if radius_km <= 0 or radius_km > 50:
            raise ValueError("O raio deve estar entre 0 e 50 km")
        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            raise ValueError("Coordenadas inválidas")
            
        return await self.repository.find_nearby(lat, lng, radius_km, limit)
