from decimal import Decimal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Bid(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    campaign_id: str
    amount: Decimal = Field(..., gt=0, decimal_places=2)


class Impression(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    campaign_id: str


class Click(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    campaign_id: str
