from domain.entities import LocationEvent
from domain.repositories import GeoRepository

class ProcessLocationEventUseCase:
    def __init__(self, geo_repository: GeoRepository):
        self.geo_repository = geo_repository

    async def execute(self, event: LocationEvent) -> None:
        if event.status == "offline":
            await self.geo_repository.remove_location(event.driver_id)
        else:
            await self.geo_repository.update_location(event)
