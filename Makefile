.PHONY: up down logs run-simulator

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f

run-simulator:
	cd simulator && uv run python main.py
