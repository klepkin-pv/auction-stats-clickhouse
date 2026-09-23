from dataclasses import dataclass
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from src.cache import cache_key, get_stats, invalidate_stats, set_stats
from src.clickhouse.client import get_client
from src.models.bid import Bid, Click, Impression

router = APIRouter()

MAX_LIMIT = 500
DEFAULT_LIMIT = 50


@dataclass(frozen=True)
class StatsFilters:
    campaign_id: str | None = None
    date_from: str | None = None
    date_to: str | None = None
    limit: int = DEFAULT_LIMIT
    offset: int = 0

    def as_key(self) -> dict:
        return {
            "campaign_id": self.campaign_id or "all",
            "date_from": self.date_from or "none",
            "date_to": self.date_to or "none",
            "limit": self.limit,
            "offset": self.offset,
        }


def _ch_datetime(value: datetime) -> str:
    """Timestamp in the naive UTC format ClickHouse keeps in DateTime columns."""
    if value.tzinfo is not None:
        value = value.astimezone(UTC).replace(tzinfo=None)
    return value.strftime("%Y-%m-%d %H:%M:%S")


def stats_filters(
    campaign_id: str | None = Query(None, description="Фильтр по одной кампании"),
    date_from: datetime | None = Query(
        None, description="Начало периода по created_at (ISO 8601), включительно"
    ),
    date_to: datetime | None = Query(
        None, description="Конец периода по created_at (ISO 8601), включительно"
    ),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT, description="Сколько кампаний вернуть"),
    offset: int = Query(0, ge=0, description="Смещение для пагинации"),
) -> StatsFilters:
    normalized_from = _ch_datetime(date_from) if date_from else None
    normalized_to = _ch_datetime(date_to) if date_to else None
    if normalized_from and normalized_to and normalized_from > normalized_to:
        raise HTTPException(status_code=400, detail="date_from must not be later than date_to")
    return StatsFilters(
        campaign_id=campaign_id,
        date_from=normalized_from,
        date_to=normalized_to,
        limit=limit,
        offset=offset,
    )


def _build_where(filters: StatsFilters, table_prefix: str = "") -> tuple[str, dict]:
    conditions = []
    params = {}
    if filters.campaign_id:
        conditions.append(f"{table_prefix}campaign_id = %(campaign_id)s")
        params["campaign_id"] = filters.campaign_id
    if filters.date_from:
        conditions.append(f"{table_prefix}created_at >= toDateTime(%(date_from)s)")
        params["date_from"] = filters.date_from
    if filters.date_to:
        conditions.append(f"{table_prefix}created_at <= toDateTime(%(date_to)s)")
        params["date_to"] = filters.date_to
    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    return where, params


def _pagination(filters: StatsFilters) -> str:
    # limit и offset уже ограничены в stats_filters (ge/le), поэтому подставляем их как числа
    return f"LIMIT {filters.limit} OFFSET {filters.offset}"


def _rows_to_stats(rows, fields):
    return [dict(zip(fields, row, strict=False)) for row in rows]


def _cached(name: str, filters: StatsFilters, sql: str, params: dict, fields: list[str]):
    key = cache_key(f"stats:{name}", filters.as_key())
    cached = get_stats(key)
    if cached is not None:
        return cached

    result = get_client().query(sql, parameters=params)
    stats = _rows_to_stats(result.result_rows, fields)
    set_stats(key, stats)
    return stats


@router.post("/bids")
def create_bids(bids: list[Bid]):
    client = get_client()
    rows = [
        (str(b.id), b.campaign_id, float(b.amount), b.created_at)
        for b in bids
    ]
    client.insert("bids", rows)
    invalidate_stats()
    return {"inserted": len(rows)}


@router.post("/impressions")
def create_impressions(items: list[Impression]):
    client = get_client()
    rows = [(str(i.id), i.campaign_id, i.created_at) for i in items]
    client.insert("impressions", rows)
    invalidate_stats()
    return {"inserted": len(rows)}


@router.post("/clicks")
def create_clicks(items: list[Click]):
    client = get_client()
    rows = [(str(c.id), c.campaign_id, c.created_at) for c in items]
    client.insert("clicks", rows)
    invalidate_stats()
    return {"inserted": len(rows)}


@router.get("/stats/ctr")
def get_ctr(filters: StatsFilters = Depends(stats_filters)):
    where, params = _build_where(filters, table_prefix="i.")
    sql = f"""
        SELECT
            i.campaign_id,
            count() AS impressions,
            countIf(c.id IS NOT NULL) AS clicks,
            round(countIf(c.id IS NOT NULL) / count(), 4) AS ctr
        FROM impressions i
        LEFT JOIN clicks c ON i.id = c.id
        {where}
        GROUP BY i.campaign_id
        ORDER BY i.campaign_id
        {_pagination(filters)}
    """
    return _cached(
        "ctr",
        filters,
        sql,
        params,
        ["campaign_id", "impressions", "clicks", "ctr"],
    )


@router.get("/stats/revenue")
def get_revenue(filters: StatsFilters = Depends(stats_filters)):
    where, params = _build_where(filters)
    sql = f"""
        SELECT campaign_id, toFloat64(round(sum(amount), 2)) AS revenue
        FROM bids
        {where}
        GROUP BY campaign_id
        ORDER BY campaign_id
        {_pagination(filters)}
    """
    return _cached(
        "revenue",
        filters,
        sql,
        params,
        ["campaign_id", "revenue"],
    )


@router.get("/stats/cpm")
def get_cpm(filters: StatsFilters = Depends(stats_filters)):
    where, params = _build_where(filters)
    sql = f"""
        SELECT campaign_id, toFloat64(round(sum(amount) / count() * 1000, 2)) AS cpm
        FROM bids
        {where}
        GROUP BY campaign_id
        ORDER BY campaign_id
        {_pagination(filters)}
    """
    return _cached(
        "cpm",
        filters,
        sql,
        params,
        ["campaign_id", "cpm"],
    )
