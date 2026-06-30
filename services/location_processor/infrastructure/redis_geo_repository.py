import redis.asyncio as redis
from domain.entities import LocationEvent
from domain.repositories import GeoRepository

class RedisGeoRepository(GeoRepository):
    def __init__(self, client: redis.Redis, geo_key: str = "drivers:locations"):
        self.client = client
        self.geo_key = geo_key

    async def update_location(self, event: LocationEvent) -> None:
        await self.client.geoadd(self.geo_key, (event.lng, event.lat, event.driver_id))

    async def remove_location(self, driver_id: str) -> None:
        await self.client.zrem(self.geo_key, driver_id)
