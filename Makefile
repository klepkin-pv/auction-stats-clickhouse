.PHONY: up down test lint fmt seed

up:
	docker compose up --build -d

down:
	docker compose down -v

test:
	pytest

lint:
	ruff check src tests scripts

fmt:
	ruff format src tests scripts

seed:
	python scripts/generate_events.py
