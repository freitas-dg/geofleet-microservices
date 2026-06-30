import asyncio
import random
import time
import httpx
from typing import List, Dict

NUM_DRIVERS = 100
TICK_INTERVAL_SECONDS = 4.0
INGEST_URL = "http://localhost:8001/locations/"
SEARCH_URL = "http://localhost:8002/search/nearby"

BASE_LAT = -23.5505
BASE_LNG = -46.6333

def generate_initial_drivers() -> List[Dict]:
    drivers = []
    for i in range(1, NUM_DRIVERS + 1):
        drivers.append({
            "driver_id": f"sim-driver-{i}",
            "lat": BASE_LAT + random.uniform(-0.05, 0.05),
            "lng": BASE_LNG + random.uniform(-0.05, 0.05),
            "status": "available"
        })
    return drivers

def perform_random_walk(drivers: List[Dict]):
    for driver in drivers:
        driver["lat"] += random.uniform(-0.0005, 0.0005)
        driver["lng"] += random.uniform(-0.0005, 0.0005)

async def send_location(client: httpx.AsyncClient, driver: Dict):
    try:
        await client.post(INGEST_URL, json=driver)
    except httpx.RequestError as e:
        print(f"[!] Erro ao enviar localização do motorista {driver['driver_id']}: {e}")

async def perform_search(client: httpx.AsyncClient):
    try:
        start_time = time.time()
        response = await client.get(
            SEARCH_URL,
            params={"lat": BASE_LAT, "lng": BASE_LNG, "radius_km": 10.0}
        )
        elapsed = (time.time() - start_time) * 1000
        if response.status_code == 200:
            data = response.json()
            num_results = len(data.get("results", []))
            print(f"[SEARCH] Encontrou {num_results} motoristas em {elapsed:.2f}ms")
        else:
            print(f"[!] Erro na busca: {response.status_code}")
    except httpx.RequestError as e:
        print(f"[!] Erro de conexão na busca: {e}")

async def main():
    print(f"Iniciando simulador com {NUM_DRIVERS} motoristas...")
    drivers = generate_initial_drivers()
    tick_count = 0

    async with httpx.AsyncClient() as client:
        while True:
            tick_start = time.time()
            perform_random_walk(drivers)
            
            print(f"\n--- Tick {tick_count} ---")
            
            tasks = [send_location(client, d) for d in drivers]
            await asyncio.gather(*tasks)
            print(f"[*] {NUM_DRIVERS} localizações enviadas.")

            if tick_count % 3 == 0:
                await perform_search(client)
            
            tick_count += 1
            
            elapsed = time.time() - tick_start
            sleep_time = max(0.0, TICK_INTERVAL_SECONDS - elapsed)
            await asyncio.sleep(sleep_time)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSimulador interrompido pelo usuário.")
