from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.routes import router as ingest_router
from infrastructure.redis_connection import redis_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await redis_client.aclose()

app = FastAPI(
    title="GeoFleet Location Ingest Service",
    description="High throughput location ingestion via Redis Streams",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(ingest_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
