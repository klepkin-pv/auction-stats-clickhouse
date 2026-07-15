from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass
class Bid:
    bid_id: UUID
    lot_id: str
    bidder_id: str
    amount: Decimal
    created_at: datetime | None = None
