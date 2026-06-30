import uuid
from typing import List, Optional
from domain.entities import Driver
from domain.repositories import DriverRepository

class DriverServiceUseCases:
    def __init__(self, repository: DriverRepository):
        self.repository = repository

    async def register_driver(self, name: str) -> Driver:
        driver_id = f"driver-{uuid.uuid4()}"
        driver = Driver(id=driver_id, name=name, status="offline")
        return await self.repository.create(driver)

    async def get_driver(self, driver_id: str) -> Optional[Driver]:
        return await self.repository.get_by_id(driver_id)

    async def update_driver_status(self, driver_id: str, status: str) -> Optional[Driver]:
        if status not in ["available", "busy", "offline"]:
            raise ValueError("Invalid status")
        return await self.repository.update_status(driver_id, status)

    async def list_all_drivers(self) -> List[Driver]:
        return await self.repository.list_all()
