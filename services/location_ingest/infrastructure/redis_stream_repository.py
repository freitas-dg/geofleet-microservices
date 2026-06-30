import json
import redis.asyncio as redis
from domain.entities import LocationEvent
from domain.repositories import LocationEventPublisher

class RedisStreamPublisher(LocationEventPublisher):
    def __init__(self, client: redis.Redis, stream_name: str = "driver_locations"):
        self.client = client
        self.stream_name = stream_name

    async def publish(self, event: LocationEvent) -> str:
        data = {
            "driver_id": event.driver_id,
            "lat": str(event.lat),
            "lng": str(event.lng),
            "status": event.status or ""
        }
        message_id = await self.client.xadd(self.stream_name, data)
        return message_id
