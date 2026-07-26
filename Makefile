.PHONY: up down test lint fmt

up:
	docker compose up --build -d

down:
	docker compose down -v

test:
	pytest

lint:
	ruff check src tests

fmt:
	ruff format src tests
