from fastapi import APIRouter

from src.cache import cache_key, get_stats, invalidate_stats, set_stats
from src.clickhouse.client import get_client
from src.models.bid import Bid, Click, Impression

router = APIRouter()


def _build_filter(campaign_id: str | None) -> tuple[str, dict]:
    if campaign_id:
        return "WHERE campaign_id = %(campaign_id)s", {"campaign_id": campaign_id}
    return "", {}


def _rows_to_stats(rows, fields):
    return [dict(zip(fields, row, strict=False)) for row in rows]


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
def get_ctr(campaign_id: str | None = None):
    key = cache_key("stats:ctr", {"campaign_id": campaign_id or "all"})
    cached = get_stats(key)
    if cached is not None:
        return cached

    client = get_client()
    where, params = _build_filter(campaign_id)
    result = client.query(
        f"""
        SELECT
            i.campaign_id,
            count() AS impressions,
            countIf(c.id IS NOT NULL) AS clicks,
            round(countIf(c.id IS NOT NULL) / count(), 4) AS ctr
        FROM impressions i
        LEFT JOIN clicks c ON i.id = c.id
        {where.replace("campaign_id", "i.campaign_id")}
        GROUP BY i.campaign_id
        ORDER BY i.campaign_id
        """,
        parameters=params,
    )
    stats = _rows_to_stats(
        result.result_rows,
        ["campaign_id", "impressions", "clicks", "ctr"],
    )
    set_stats(key, stats)
    return stats


@router.get("/stats/revenue")
def get_revenue(campaign_id: str | None = None):
    key = cache_key("stats:revenue", {"campaign_id": campaign_id or "all"})
    cached = get_stats(key)
    if cached is not None:
        return cached

    client = get_client()
    where, params = _build_filter(campaign_id)
    result = client.query(
        f"""
        SELECT campaign_id, round(sum(amount), 2) AS revenue
        FROM bids
        {where}
        GROUP BY campaign_id
        ORDER BY campaign_id
        """,
        parameters=params,
    )
    stats = [
        {"campaign_id": row[0], "revenue": float(row[1])}
        for row in result.result_rows
    ]
    set_stats(key, stats)
    return stats


@router.get("/stats/cpm")
def get_cpm(campaign_id: str | None = None):
    key = cache_key("stats:cpm", {"campaign_id": campaign_id or "all"})
    cached = get_stats(key)
    if cached is not None:
        return cached

    client = get_client()
    where, params = _build_filter(campaign_id)
    result = client.query(
        f"""
        SELECT
            campaign_id,
            round(sum(amount) / count() * 1000, 2) AS cpm
        FROM bids
        {where}
        GROUP BY campaign_id
        ORDER BY campaign_id
        """,
        parameters=params,
    )
    stats = [
        {"campaign_id": row[0], "cpm": float(row[1])}
        for row in result.result_rows
    ]
    set_stats(key, stats)
    return stats
