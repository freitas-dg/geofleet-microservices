from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from domain.entities import Driver
from domain.repositories import DriverRepository
from infrastructure.models import DriverModel

class PostgresDriverRepository(DriverRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, driver: Driver) -> Driver:
        driver_model = DriverModel.from_domain(driver)
        self.session.add(driver_model)
        await self.session.commit()
        await self.session.refresh(driver_model)
        return driver_model.to_domain()

    async def get_by_id(self, driver_id: str) -> Optional[Driver]:
        result = await self.session.execute(select(DriverModel).where(DriverModel.id == driver_id))
        driver_model = result.scalars().first()
        return driver_model.to_domain() if driver_model else None

    async def update_status(self, driver_id: str, status: str) -> Optional[Driver]:
        result = await self.session.execute(select(DriverModel).where(DriverModel.id == driver_id))
        driver_model = result.scalars().first()
        if not driver_model:
            return None
        
        driver_model.status = status
        await self.session.commit()
        await self.session.refresh(driver_model)
        return driver_model.to_domain()

    async def list_all(self) -> List[Driver]:
        result = await self.session.execute(select(DriverModel))
        models = result.scalars().all()
        return [m.to_domain() for m in models]

    async def find_nearby(self, lat: float, lng: float, radius_km: float) -> List[Driver]:
        from sqlalchemy import func
        distance_col = (
            6371.0 * func.acos(
                func.cos(func.radians(lat)) *
                func.cos(func.radians(DriverModel.latitude)) *
                func.cos(func.radians(DriverModel.longitude) - func.radians(lng)) +
                func.sin(func.radians(lat)) *
                func.sin(func.radians(DriverModel.latitude))
            )
        )
        query = (
            select(DriverModel)
            .where(DriverModel.latitude.isnot(None))
            .where(DriverModel.longitude.isnot(None))
            .where(distance_col < radius_km)
            .order_by(distance_col.asc())
        )
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [m.to_domain() for m in models]

