from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.routes import router as driver_router
from infrastructure.database import engine, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(
    title="GeoFleet Driver Service",
    description="Driver management microservice for GeoFleet",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(driver_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
