# Auction Stats ClickHouse

![CI](https://github.com/klepkin-pv/auction-stats-clickhouse/actions/workflows/ci.yml/badge.svg)

Pet project for practicing ClickHouse and FastAPI.

A small service that receives auction bids, stores raw events in ClickHouse, and serves aggregated statistics through a REST API.

## Stack

- Python 3.12
- FastAPI
- ClickHouse
- SQLAlchemy 2.0 (async)
- Pydantic v2
- pytest
- Docker Compose

## Architecture

- `POST /bids` — accept a new bid.
- `GET /stats` — return aggregated stats: total bids, average bid, max bid, unique bidders per lot.
- Background ETL task materializes raw events into an aggregated view.
- ClickHouse tables:
  - `bids_raw` — incoming events.
  - `bids_stats` — pre-aggregated metrics, refreshed periodically.

## Run locally

```bash
docker compose up --build
```

API will be available at http://localhost:8000/docs.

## Tests

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest
```

CI runs `ruff` and `pytest` in GitHub Actions for every push and pull request.

## Project structure

```
app/
├── api/
│   └── routes.py
├── core/
│   └── config.py
├── db/
│   ├── clickhouse.py
│   └── models.py
├── etl/
│   └── aggregator.py
├── main.py
└── schemas.py
docker-compose.yml
Dockerfile
pytest.ini
requirements.txt
```
