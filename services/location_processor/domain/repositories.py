from typing import Protocol, List
from domain.entities import LocationEvent

class GeoRepository(Protocol):
    async def update_location(self, event: LocationEvent) -> None:
        ...

    async def remove_location(self, driver_id: str) -> None:
        ...
