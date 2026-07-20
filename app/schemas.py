from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BidIn(BaseModel):
    lot_id: str = Field(..., min_length=1, max_length=64)
    bidder_id: str = Field(..., min_length=1, max_length=64)
    amount: Decimal = Field(..., gt=0, decimal_places=2)


class BidOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    bid_id: UUID
    lot_id: str
    bidder_id: str
    amount: Decimal


class StatsOut(BaseModel):
    lot_id: str
    total_bids: int
    avg_amount: Decimal
    max_amount: Decimal
    unique_bidders: int


class HealthOut(BaseModel):
    status: str
    database: str
