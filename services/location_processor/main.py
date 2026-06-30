import asyncio
import logging
from infrastructure.redis_connection import redis_client
from infrastructure.redis_geo_repository import RedisGeoRepository
from use_cases.processor_use_cases import ProcessLocationEventUseCase
from domain.entities import LocationEvent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("location-processor")

STREAM_NAME = "driver_locations"
GROUP_NAME = "processor_group"

async def ensure_consumer_group():
    try:
        await redis_client.xgroup_create(STREAM_NAME, GROUP_NAME, id="0", mkstream=True)
        logger.info(f"Consumer group '{GROUP_NAME}' created.")
    except Exception as e:
        if "BUSYGROUP" in str(e):
            pass
        else:
            logger.error(f"Error creating consumer group: {e}")

async def process_stream():
    await ensure_consumer_group()
    geo_repo = RedisGeoRepository(redis_client)
    use_case = ProcessLocationEventUseCase(geo_repo)

    logger.info("Starting location processor loop...")
    while True:
        try:
            messages = await redis_client.xreadgroup(
                groupname=GROUP_NAME,
                consumername="worker-1",
                streams={STREAM_NAME: ">"},
                count=10,
                block=2000
            )

            if not messages:
                continue

            for stream, msgs in messages:
                for message_id, data in msgs:
                    event = LocationEvent(
                        driver_id=data.get("driver_id"),
                        lat=float(data.get("lat")),
                        lng=float(data.get("lng")),
                        status=data.get("status")
                    )
                    await use_case.execute(event)
                    await redis_client.xack(STREAM_NAME, GROUP_NAME, message_id)
        except Exception as e:
            logger.error(f"Error processing stream: {e}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(process_stream())
    except KeyboardInterrupt:
        logger.info("Shutting down processor...")
