.PHONY: up down logs run-simulator benchmark

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f

run-simulator:
	cd simulator && uv run python main.py

benchmark:
	docker compose run --rm --build benchmark-runner
