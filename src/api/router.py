from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, HTTPException

from src.clickhouse.client import get_client
from src.models.bid import Bid, Click, Impression

router = APIRouter()


@router.post("/bids")
def create_bids(bids: list[Bid]):
    client = get_client()
    rows = [
        (str(b.id), b.campaign_id, float(b.amount))
        for b in bids
    ]
    client.insert("bids", rows, database="auction")
    return {"inserted": len(rows)}


@router.post("/impressions")
def create_impressions(items: list[Impression]):
    client = get_client()
    rows = [(str(i.id), i.campaign_id) for i in items]
    client.insert("impressions", rows, database="auction")
    return {"inserted": len(rows)}


@router.post("/clicks")
def create_clicks(items: list[Click]):
    client = get_client()
    rows = [(str(c.id), c.campaign_id) for c in items]
    client.insert("clicks", rows, database="auction")
    return {"inserted": len(rows)}


@router.get("/stats/ctr")
def get_ctr(campaign_id: str | None = None):
    client = get_client()
    where = "WHERE campaign_id = %(campaign_id)s" if campaign_id else ""
    params = {"campaign_id": campaign_id} if campaign_id else {}
    result = client.query(
        f"""
        SELECT
            campaign_id,
            count() AS impressions,
            sum(is_click) AS clicks,
            round(sum(is_click) / count(), 4) AS ctr
        FROM (
            SELECT
                campaign_id,
                1 AS is_click
            FROM clicks
            {where}
            UNION ALL
            SELECT
                campaign_id,
                0 AS is_click
            FROM impressions
            {where}
        )
        GROUP BY campaign_id
        ORDER BY campaign_id
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
    where = "WHERE campaign_id = %(campaign_id)s" if campaign_id else ""
    params = {"campaign_id": campaign_id} if campaign_id else {}
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
