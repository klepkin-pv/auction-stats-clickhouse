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

Эндпоинты `GET /stats/*` принимают общие параметры:

- `campaign_id` — фильтр по одной кампании;
- `date_from`, `date_to` — период по `created_at` (ISO 8601, границы включительно);
- `limit` — сколько кампаний вернуть, от 1 до 500 (по умолчанию 50);
- `offset` — смещение для пагинации (по умолчанию 0).

```bash
curl "http://localhost:8000/api/v1/stats/ctr?date_from=2026-09-01T00:00:00Z&date_to=2026-09-02T00:00:00Z"
curl "http://localhost:8000/api/v1/stats/revenue?campaign_id=cmp-1&limit=10&offset=10"
```

## Тестовые данные

`scripts/generate_events.py` наполняет сервис ставками, показами и кликами. Клик переиспользует `id` показа, поэтому CTR и CPM считаются на связанных данных.

```bash
# 1000 ставок, 5000 показов, 5% кликов за последние сутки
python scripts/generate_events.py

# воспроизводимый набор за трое суток, без отправки в сервис
python scripts/generate_events.py --bids 500 --window-hours 72 --seed 42 --dry-run

# поток с паузой между пакетами
python scripts/generate_events.py --bids 2000 --interval 1
```

Параметры: `--bids`, `--impressions`, `--campaigns`, `--click-rate`, `--window-hours`, `--batch-size`, `--interval`, `--seed`, `--dry-run`. Полный список — `python scripts/generate_events.py --help`, запуск через Makefile — `make seed`.

## Тесты

```bash
make test
```
