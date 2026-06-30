import asyncio
import time
import random
import httpx
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import redis.asyncio as redis

NUM_DRIVERS = 10000
NUM_REQUESTS = 1000
CONCURRENCY = 100

PG_URL = "postgresql+asyncpg://geofleet_user:geofleet_password@localhost:5432/geofleet_db"
REDIS_URL = "redis://localhost:6379/0"
GEO_KEY = "drivers:locations"

DRIVER_API_URL = "http://localhost:8000/drivers/nearby"
SEARCH_API_URL = "http://localhost:8002/search/nearby"

BASE_LAT = -23.5505
BASE_LNG = -46.6333

async def seed_data():
    engine = create_async_engine(PG_URL)
    r_client = redis.from_url(REDIS_URL, decode_responses=True)

    print("Limpando dados antigos...")
    async with engine.begin() as conn:
        await conn.execute(text("DELETE FROM drivers"))
    await r_client.delete(GEO_KEY)

    print(f"Semeando {NUM_DRIVERS} motoristas...")
    
    pg_values = []
    redis_data = []

    for i in range(NUM_DRIVERS):
        d_id = f"bench-driver-{i}"
        lat = BASE_LAT + random.uniform(-0.1, 0.1)
        lng = BASE_LNG + random.uniform(-0.1, 0.1)
        
        pg_values.append({
            "id": d_id,
            "name": f"Driver {i}",
            "status": "available",
            "lat": lat,
            "lng": lng
        })
        
        redis_data.extend([lng, lat, d_id])

    async with engine.begin() as conn:
        query = text("""
            INSERT INTO drivers (id, name, status, latitude, longitude)
            VALUES (:id, :name, :status, :lat, :lng)
        """)
        await conn.execute(query, pg_values)
        
    await r_client.execute_command("GEOADD", GEO_KEY, *redis_data)

    await engine.dispose()
    await r_client.aclose()
    print("Semeio concluído!")

async def fetch_api(client: httpx.AsyncClient, url: str):
    lat = BASE_LAT + random.uniform(-0.05, 0.05)
    lng = BASE_LNG + random.uniform(-0.05, 0.05)
    
    start = time.time()
    resp = await client.get(url, params={"lat": lat, "lng": lng, "radius_km": 5.0})
    latency = (time.time() - start) * 1000
    
    return latency, resp.status_code

async def run_benchmark(name: str, url: str):
    print(f"\nIniciando benchmark: {name}")
    latencies = []
    
    async with httpx.AsyncClient(limits=httpx.Limits(max_connections=CONCURRENCY)) as client:
        tasks = []
        for _ in range(NUM_REQUESTS):
            tasks.append(fetch_api(client, url))
        
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time

    for lat, status in results:
        if status == 200:
            latencies.append(lat)

    if not latencies:
        print("Nenhuma requisição teve sucesso!")
        return

    latencies.sort()
    avg = sum(latencies) / len(latencies)
    p99 = latencies[int(len(latencies) * 0.99)]
    
    print(f"Resultados para {name}:")
    print(f"Total de Requisições : {len(latencies)} com sucesso")
    print(f"Tempo Total          : {total_time:.2f}s")
    print(f"Throughput           : {len(latencies) / total_time:.2f} req/s")
    print(f"Latência Média       : {avg:.2f}ms")
    print(f"Latência P99         : {p99:.2f}ms")

async def main():
    await seed_data()
    print("\nAguardando 3 segundos para estabilização...")
    await asyncio.sleep(3)
    
    await run_benchmark("PostgreSQL (Haversine)", DRIVER_API_URL)
    await run_benchmark("Redis GEO (Em memória)", SEARCH_API_URL)

if __name__ == "__main__":
    asyncio.run(main())
