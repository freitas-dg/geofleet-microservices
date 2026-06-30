from fastapi import APIRouter, Depends, Query, HTTPException, status
from api.schemas import NearbySearchResponse, DriverLocationResponse
from api.dependencies import get_search_use_case
from use_cases.search_use_cases import SearchNearbyUseCase

router = APIRouter(prefix="/search", tags=["search"])

@router.get("/nearby", response_model=NearbySearchResponse)
async def search_nearby(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(..., gt=0, le=50),
    use_case: SearchNearbyUseCase = Depends(get_search_use_case)
):
    try:
        results = await use_case.execute(lat, lng, radius_km)
        response_list = [
            DriverLocationResponse(
                driver_id=r.driver_id,
                lat=r.lat,
                lng=r.lng,
                distance_km=r.distance_km
            ) for r in results
        ]
        return NearbySearchResponse(results=response_list)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
