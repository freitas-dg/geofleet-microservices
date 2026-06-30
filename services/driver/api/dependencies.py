from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.database import get_db
from infrastructure.postgres_repository import PostgresDriverRepository
from use_cases.driver_use_cases import DriverServiceUseCases

def get_driver_repository(session: AsyncSession = Depends(get_db)) -> PostgresDriverRepository:
    return PostgresDriverRepository(session)

def get_driver_use_cases(
    repository: PostgresDriverRepository = Depends(get_driver_repository)
) -> DriverServiceUseCases:
    return DriverServiceUseCases(repository)
