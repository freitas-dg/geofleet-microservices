from typing import Protocol
from domain.entities import LocationEvent

class LocationEventPublisher(Protocol):
    async def publish(self, event: LocationEvent) -> str:
        ...
