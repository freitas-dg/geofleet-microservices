from dataclasses import dataclass
from typing import Optional

@dataclass
class Driver:
    id: str
    name: str
    status: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
