from fastapi import APIRouter, Depends, status
from api.schemas import LocationPayload, IngestResponse
from api.dependencies import get_ingest_use_case
from use_cases.ingest_use_cases import IngestLocationUseCase
from domain.entities import LocationEvent

router = APIRouter(prefix="/locations", tags=["locations"])

@router.post("/", response_model=IngestResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_location(
    payload: LocationPayload,
    use_case: IngestLocationUseCase = Depends(get_ingest_use_case)
):
    event = LocationEvent(
        driver_id=payload.driver_id,
        lat=payload.lat,
        lng=payload.lng,
        status=payload.status
    )
    message_id = await use_case.execute(event)
    return IngestResponse(success=True, message_id=message_id)
