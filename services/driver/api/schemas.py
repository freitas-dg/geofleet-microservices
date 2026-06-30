from pydantic import BaseModel
from typing import Optional

class DriverCreate(BaseModel):
    name: str

class DriverStatusUpdate(BaseModel):
    status: str

class DriverResponse(BaseModel):
    id: str
    name: str
    status: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    class Config:
        from_attributes = True
