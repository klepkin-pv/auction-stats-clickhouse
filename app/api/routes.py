from decimal import Decimal
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.db.clickhouse import get_client
from app.etl.aggregator import aggregate_lot_stats
from app.schemas import BidIn, BidOut, StatsOut

router = APIRouter()


@router.post("/bids", response_model=BidOut)
def create_bid(payload: BidIn) -> BidOut:
    client = get_client()
    bid_id = uuid4()
    client.execute(
        "INSERT INTO bids_raw (bid_id, lot_id, bidder_id, amount) VALUES",
        [(bid_id, payload.lot_id, payload.bidder_id, payload.amount)],
    )
    return BidOut(
        bid_id=bid_id,
        lot_id=payload.lot_id,
        bidder_id=payload.bidder_id,
        amount=payload.amount,
    )


@router.get("/stats/{lot_id}", response_model=StatsOut)
def get_stats(lot_id: str) -> StatsOut:
    client = get_client()
    rows = client.execute(
        "SELECT lot_id, total_bids, avg_amount, max_amount, unique_bidders "
        "FROM bids_stats WHERE lot_id = %(lot_id)s",
        {"lot_id": lot_id},
    )
    if not rows:
        aggregate_lot_stats(lot_id)
        rows = client.execute(
            "SELECT lot_id, total_bids, avg_amount, max_amount, unique_bidders "
            "FROM bids_stats WHERE lot_id = %(lot_id)s",
            {"lot_id": lot_id},
        )
    if not rows:
        raise HTTPException(status_code=404, detail="Lot not found")
    row = rows[0]
    return StatsOut(
        lot_id=row[0],
        total_bids=row[1],
        avg_amount=Decimal(row[2]),
        max_amount=Decimal(row[3]),
        unique_bidders=row[4],
    )
