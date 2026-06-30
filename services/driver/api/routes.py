from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from api.schemas import DriverCreate, DriverResponse, DriverStatusUpdate
from api.dependencies import get_driver_use_cases
from use_cases.driver_use_cases import DriverServiceUseCases

router = APIRouter(prefix="/drivers", tags=["drivers"])

@router.post("/", response_model=DriverResponse, status_code=status.HTTP_201_CREATED)
async def create_driver(
    driver_in: DriverCreate,
    use_cases: DriverServiceUseCases = Depends(get_driver_use_cases)
):
    return await use_cases.register_driver(driver_in.name)

@router.get("/", response_model=List[DriverResponse])
async def list_drivers(
    use_cases: DriverServiceUseCases = Depends(get_driver_use_cases)
):
    return await use_cases.list_all_drivers()

@router.get("/nearby", response_model=List[DriverResponse])
async def search_nearby(
    lat: float,
    lng: float,
    radius_km: float,
    use_cases: DriverServiceUseCases = Depends(get_driver_use_cases)
):
    try:
        return await use_cases.search_nearby_drivers(lat, lng, radius_km)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{driver_id}", response_model=DriverResponse)
async def get_driver(
    driver_id: str,
    use_cases: DriverServiceUseCases = Depends(get_driver_use_cases)
):
    driver = await use_cases.get_driver(driver_id)
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found")
    return driver

@router.patch("/{driver_id}/status", response_model=DriverResponse)
async def update_driver_status(
    driver_id: str,
    status_update: DriverStatusUpdate,
    use_cases: DriverServiceUseCases = Depends(get_driver_use_cases)
):
    try:
        driver = await use_cases.update_driver_status(driver_id, status_update.status)
        if not driver:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found")
        return driver
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
