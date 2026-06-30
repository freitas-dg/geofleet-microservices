from dataclasses import dataclass

@dataclass
class DriverLocation:
    driver_id: str
    lat: float
    lng: float
    distance_km: float
