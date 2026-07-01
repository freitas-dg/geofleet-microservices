from fastapi import APIRouter, Depends, Query, HTTPException, status
from api.schemas import NearbySearchResponse, DriverLocationResponse
from api.dependencies import get_search_use_case
from use_cases.search_use_cases import SearchNearbyUseCase

router = APIRouter(prefix="/search", tags=["search"])

@router.get("/nearby")
async def search_nearby(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(..., gt=0, le=50),
    limit: int = Query(50, ge=1, le=1000),
    use_case: SearchNearbyUseCase = Depends(get_search_use_case)
):
    try:
        results = await use_case.execute(lat, lng, radius_km, limit)
        return {"results": results}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
