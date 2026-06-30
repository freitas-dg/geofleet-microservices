from fastapi import Depends
import redis.asyncio as redis
from infrastructure.redis_connection import get_redis_client
from infrastructure.redis_geo_repository import RedisSearchRepository
from use_cases.search_use_cases import SearchNearbyUseCase

def get_search_repository(client: redis.Redis = Depends(get_redis_client)) -> RedisSearchRepository:
    return RedisSearchRepository(client)

def get_search_use_case(
    repository: RedisSearchRepository = Depends(get_search_repository)
) -> SearchNearbyUseCase:
    return SearchNearbyUseCase(repository)
