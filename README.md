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
