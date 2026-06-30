from domain.entities import LocationEvent
from domain.repositories import LocationEventPublisher

class IngestLocationUseCase:
    def __init__(self, publisher: LocationEventPublisher):
        self.publisher = publisher

    async def execute(self, event: LocationEvent) -> str:
        return await self.publisher.publish(event)
