import redis.asyncio as redis
from typing import List
from domain.entities import DriverLocation
from domain.repositories import SearchRepository

class RedisSearchRepository(SearchRepository):
    def __init__(self, client: redis.Redis, geo_key: str = "drivers:locations"):
        self.client = client
        self.geo_key = geo_key

    async def find_nearby(self, lat: float, lng: float, radius_km: float, limit: int = 50) -> List[dict]:
        results = await self.client.geosearch(
            name=self.geo_key,
            longitude=lng,
            latitude=lat,
            radius=radius_km,
            unit="km",
            withdist=True,
            withcoord=True,
            sort="ASC",
            count=limit
        )
        
        drivers = []
        for member, distance, (member_lng, member_lat) in results:
            drivers.append({
                "driver_id": member,
                "lat": member_lat,
                "lng": member_lng,
                "distance_km": distance
            })
        return drivers
