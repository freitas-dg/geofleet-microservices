from sqlalchemy import Column, String, Float
from infrastructure.database import Base
from domain.entities import Driver

class DriverModel(Base):
    __tablename__ = "drivers"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    def to_domain(self) -> Driver:
        return Driver(
            id=self.id,
            name=self.name,
            status=self.status,
            latitude=self.latitude,
            longitude=self.longitude
        )

    @staticmethod
    def from_domain(driver: Driver) -> "DriverModel":
        return DriverModel(
            id=driver.id,
            name=driver.name,
            status=driver.status,
            latitude=driver.latitude,
            longitude=driver.longitude
        )
