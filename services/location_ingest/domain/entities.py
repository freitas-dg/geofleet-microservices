from dataclasses import dataclass
from typing import Optional

@dataclass
class LocationEvent:
    driver_id: str
    lat: float
    lng: float
    status: Optional[str] = None
