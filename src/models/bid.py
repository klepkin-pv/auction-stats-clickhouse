from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Bid(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    campaign_id: str
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Impression(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    campaign_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Click(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    campaign_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
