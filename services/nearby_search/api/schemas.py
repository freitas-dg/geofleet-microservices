from pydantic import BaseModel
from typing import List

class DriverLocationResponse(BaseModel):
    driver_id: str
    lat: float
    lng: float
    distance_km: float

class NearbySearchResponse(BaseModel):
    results: List[DriverLocationResponse]
