from decimal import Decimal
from uuid import uuid4

from src.models.bid import Bid


def test_bid_requires_positive_amount():
    bid = Bid(campaign_id="cmp-1", amount=Decimal("10.00"))
    assert bid.campaign_id == "cmp-1"
    assert bid.amount == Decimal("10.00")
    assert bid.id
