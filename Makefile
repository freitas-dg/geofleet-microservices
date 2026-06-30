.PHONY: up down run-driver run-ingest run-processor run-search

up:
	docker compose up -d

down:
	docker compose down

run-driver:
	cd services/driver && uv run uvicorn main:app --port 8000 --reload

run-ingest:
	cd services/location_ingest && uv run uvicorn main:app --port 8001 --reload

run-processor:
	cd services/location_processor && uv run python main.py

run-search:
	cd services/nearby_search && uv run uvicorn main:app --port 8002 --reload
