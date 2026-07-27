# auction-stats-clickhouse

Сервис статистики рекламных аукционов: сохраняет ставки, показы и клики в ClickHouse, отдаёт CTR, CPM и выручку через FastAPI.

## Стек

- Python 3.12 + FastAPI + Pydantic v2
- ClickHouse
- Redis
- Docker Compose
- pytest

## Запуск

```bash
cp .env.example .env
make up
curl http://localhost:8000/health
```

## API

- `POST /api/v1/bids` — загрузка batch ставок
- `POST /api/v1/impressions` — загрузка показов
- `POST /api/v1/clicks` — загрузка кликов
- `GET /api/v1/stats/ctr` — CTR по кампаниям
- `GET /api/v1/stats/revenue` — сумма ставок
- `GET /api/v1/stats/cpm` — CPM

## Тесты

```bash
make test
```
