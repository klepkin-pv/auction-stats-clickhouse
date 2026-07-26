# auction-stats-clickhouse

Сервис статистики рекламных аукционов на FastAPI + ClickHouse.

Хранит ставки (bids), показы (impressions) и клики (clicks), считает CTR, CPM, сумму выигранных ставок и другие метрики.

## Стек

- Python 3.12, FastAPI, Pydantic v2
- ClickHouse для аналитики
- Redis для кэширования агрегаций
- Docker Compose для локального запуска
- pytest для тестов

## Быстрый старт

```bash
# 1. Запуск
make up

# 2. Загрузка тестовых данных
python scripts/load_sample_data.py

# 3. Проверка API
curl http://localhost:8000/health
```

## API

- `POST /bids` — загрузка batch ставок
- `GET /stats/ctr` — CTR по кампаниям
- `GET /stats/revenue` — выручка (сумма победивших ставок)

## Тесты

```bash
make test
```
