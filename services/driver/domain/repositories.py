from typing import Protocol, List, Optional
from domain.entities import Driver

class DriverRepository(Protocol):
    async def create(self, driver: Driver) -> Driver:
        ...

    async def get_by_id(self, driver_id: str) -> Optional[Driver]:
        ...

    async def update_status(self, driver_id: str, status: str) -> Optional[Driver]:
        ...

    async def list_all(self) -> List[Driver]:
        ...

    async def find_nearby(self, lat: float, lng: float, radius_km: float) -> List[Driver]:
        ...
