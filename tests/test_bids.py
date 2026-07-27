from decimal import Decimal

from src.models.bid import Bid


def test_bid_has_uuid_and_positive_amount():
    bid = Bid(campaign_id="cmp-1", amount=Decimal("10.00"))
    assert bid.campaign_id == "cmp-1"
    assert bid.amount == Decimal("10.00")
    assert bid.id
