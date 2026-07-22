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

## API

- `GET /health` — healthcheck, checks ClickHouse connectivity.
- `POST /bids` — accept a new bid.
- `GET /stats/{lot_id}` — return aggregated stats for a lot: total bids, average bid, max bid, unique bidders.

## Architecture

- Raw bid events are written to ClickHouse via `POST /bids`.
- Aggregated stats are computed on demand into `bids_stats` when `GET /stats/{lot_id}` is first requested.
- ClickHouse tables:
  - `bids_raw` — incoming events.
  - `bids_stats` — pre-aggregated metrics per lot.

## Run locally

```bash
docker compose up --build
```

API will be available at http://localhost:8000/docs.

Check health:

```bash
curl http://localhost:8000/health
```

### API examples

Post a bid:

```bash
curl -X POST http://localhost:8000/bids \
  -H "Content-Type: application/json" \
  -d '{"lot_id": "lot-1", "bidder_id": "user-1", "amount": 100.50}'
```

Get aggregated stats for a lot:

```bash
curl http://localhost:8000/stats/lot-1
```

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
