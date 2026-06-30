from pydantic import BaseModel, Field
from typing import Optional

class LocationPayload(BaseModel):
    driver_id: str = Field(..., description="Unique identifier for the driver")
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lng: float = Field(..., ge=-180, le=180, description="Longitude")
    status: Optional[str] = Field(default=None, description="Current driver status")

class IngestResponse(BaseModel):
    success: bool
    message_id: str
