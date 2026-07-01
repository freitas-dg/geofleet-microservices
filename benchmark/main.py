import asyncio
import os
import time
import random
import httpx
import redis.asyncio as redis

SEARCH_API_URL = os.getenv("SEARCH_API_URL", "http://127.0.0.1:8002/search/nearby")
REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
GEO_KEY = "drivers:locations"

BASE_LAT = -23.5505
BASE_LNG = -46.6333

WARMUP_REQUESTS = 50
CONCURRENCY_LEVELS = [1, 10, 50, 100, 200]
REQUESTS_PER_LEVEL = 500
DRIVER_COUNTS = [1000, 10000, 50000]


async def seed_redis(num_drivers: int):
    r_client = redis.from_url(REDIS_URL, decode_responses=True)
    await r_client.delete(GEO_KEY)

    redis_data = []
    for i in range(num_drivers):
        lat = BASE_LAT + random.uniform(-0.1, 0.1)
        lng = BASE_LNG + random.uniform(-0.1, 0.1)
        redis_data.extend([lng, lat, f"driver-{i}"])

    batch_size = 5000
    for start in range(0, len(redis_data), batch_size * 3):
        batch = redis_data[start:start + batch_size * 3]
        if batch:
            await r_client.execute_command("GEOADD", GEO_KEY, *batch)

    count = await r_client.zcard(GEO_KEY)
    await r_client.aclose()
    return count


async def fetch(client: httpx.AsyncClient, semaphore: asyncio.Semaphore):
    lat = BASE_LAT + random.uniform(-0.05, 0.05)
    lng = BASE_LNG + random.uniform(-0.05, 0.05)

    async with semaphore:
        start = time.perf_counter()
        try:
            resp = await client.get(
                SEARCH_API_URL,
                params={"lat": lat, "lng": lng, "radius_km": 5.0}
            )
            elapsed = (time.perf_counter() - start) * 1000
            return elapsed, resp.status_code
        except httpx.RequestError:
            elapsed = (time.perf_counter() - start) * 1000
            return elapsed, 0


async def run_level(concurrency: int, num_requests: int):
    semaphore = asyncio.Semaphore(concurrency)

    async with httpx.AsyncClient(
        limits=httpx.Limits(max_connections=concurrency, max_keepalive_connections=concurrency),
        timeout=30.0
    ) as client:
        tasks = [fetch(client, semaphore) for _ in range(num_requests)]

        wall_start = time.perf_counter()
        results = await asyncio.gather(*tasks)
        wall_time = time.perf_counter() - wall_start

    latencies = []
    errors = 0
    for latency, status in results:
        if status == 200:
            latencies.append(latency)
        else:
            errors += 1

    if not latencies:
        return None

    latencies.sort()
    total = len(latencies)

    return {
        "concurrency": concurrency,
        "total": total,
        "errors": errors,
        "wall_time": wall_time,
        "throughput": total / wall_time,
        "avg": sum(latencies) / total,
        "min": latencies[0],
        "p50": latencies[int(total * 0.50)],
        "p95": latencies[int(total * 0.95)],
        "p99": latencies[int(total * 0.99)],
        "max": latencies[-1],
    }


async def warmup():
    print("  Aquecendo conexões...")
    semaphore = asyncio.Semaphore(10)
    async with httpx.AsyncClient(
        limits=httpx.Limits(max_connections=10),
        timeout=10.0
    ) as client:
        tasks = [fetch(client, semaphore) for _ in range(WARMUP_REQUESTS)]
        await asyncio.gather(*tasks)
    await asyncio.sleep(1)


def print_results_table(all_results):
    header = f"  {'Conc':>6} | {'Reqs':>6} | {'Erros':>5} | {'Throughput':>12} | {'Avg':>10} | {'P50':>10} | {'P95':>10} | {'P99':>10} | {'Max':>10}"
    separator = f"  {'─'*6}-+-{'─'*6}-+-{'─'*5}-+-{'─'*12}-+-{'─'*10}-+-{'─'*10}-+-{'─'*10}-+-{'─'*10}-+-{'─'*10}"

    print(header)
    print(separator)

    for r in all_results:
        print(
            f"  {r['concurrency']:>6} | "
            f"{r['total']:>6} | "
            f"{r['errors']:>5} | "
            f"{r['throughput']:>9.2f} r/s | "
            f"{r['avg']:>8.2f}ms | "
            f"{r['p50']:>8.2f}ms | "
            f"{r['p95']:>8.2f}ms | "
            f"{r['p99']:>8.2f}ms | "
            f"{r['max']:>8.2f}ms"
        )


async def main():
    print("=" * 80)
    print("  GeoFleet — Benchmark de Leitura (Nearby Search Service)")
    print("  Objetivo: medir throughput e latência do caminho de leitura via Redis GEO")
    print("=" * 80)

    for num_drivers in DRIVER_COUNTS:
        print(f"\n{'─' * 80}")
        print(f"  Cenário: {num_drivers:,} motoristas no Redis GEO")
        print(f"{'─' * 80}")

        count = await seed_redis(num_drivers)
        print(f"  Semeados {count:,} motoristas no Redis GEO")

        await warmup()

        all_results = []
        for concurrency in CONCURRENCY_LEVELS:
            print(f"\n  Testando concorrência = {concurrency}...")
            result = await run_level(concurrency, REQUESTS_PER_LEVEL)
            if result:
                all_results.append(result)
                print(f"    → {result['throughput']:.2f} req/s | avg={result['avg']:.2f}ms | p99={result['p99']:.2f}ms")
            else:
                print(f"    → Falhou completamente")
            await asyncio.sleep(2)

        print(f"\n  Resultados para {num_drivers:,} motoristas:")
        print()
        print_results_table(all_results)

    print(f"\n{'=' * 80}")
    print("  Benchmark concluído!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
