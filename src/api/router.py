from decimal import Decimal

from fastapi import APIRouter

from src.clickhouse.client import get_client
from src.models.bid import Bid, Click, Impression

router = APIRouter()


def _build_filter(campaign_id: str | None) -> tuple[str, dict]:
    if campaign_id:
        return "WHERE campaign_id = %(campaign_id)s", {"campaign_id": campaign_id}
    return "", {}


@router.post("/bids")
def create_bids(bids: list[Bid]):
    client = get_client()
    rows = [
        (str(b.id), b.campaign_id, float(b.amount), b.created_at)
        for b in bids
    ]
    client.insert("bids", rows)
    return {"inserted": len(rows)}


@router.post("/impressions")
def create_impressions(items: list[Impression]):
    client = get_client()
    rows = [(str(i.id), i.campaign_id, i.created_at) for i in items]
    client.insert("impressions", rows)
    return {"inserted": len(rows)}


@router.post("/clicks")
def create_clicks(items: list[Click]):
    client = get_client()
    rows = [(str(c.id), c.campaign_id, c.created_at) for c in items]
    client.insert("clicks", rows)
    return {"inserted": len(rows)}


@router.get("/stats/ctr")
def get_ctr(campaign_id: str | None = None):
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
    return [
        {
            "campaign_id": row[0],
            "impressions": row[1],
            "clicks": row[2],
            "ctr": row[3],
        }
        for row in result.result_rows
    ]


@router.get("/stats/revenue")
def get_revenue(campaign_id: str | None = None):
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
    return [
        {"campaign_id": row[0], "revenue": Decimal(str(row[1]))}
        for row in result.result_rows
    ]


@router.get("/stats/cpm")
def get_cpm(campaign_id: str | None = None):
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
    return [
        {"campaign_id": row[0], "cpm": Decimal(str(row[1]))}
        for row in result.result_rows
    ]
