from fastapi import Depends
import redis.asyncio as redis
from infrastructure.redis_connection import get_redis_client
from infrastructure.redis_stream_repository import RedisStreamPublisher
from use_cases.ingest_use_cases import IngestLocationUseCase

def get_publisher(client: redis.Redis = Depends(get_redis_client)) -> RedisStreamPublisher:
    return RedisStreamPublisher(client)

def get_ingest_use_case(
    publisher: RedisStreamPublisher = Depends(get_publisher)
) -> IngestLocationUseCase:
    return IngestLocationUseCase(publisher)
