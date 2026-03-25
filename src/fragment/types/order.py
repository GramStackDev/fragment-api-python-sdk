from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from fragment._compat import StrEnum


class OrderStatus(StrEnum):
    ALL = "all"
    PENDING = "pending"
    PROCESSING = "processing"
    RETRY = "retry"
    COMPLETED = "completed"
    FAILED = "failed"


class Order(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    service_id: int
    service_name: str
    recipient: str
    quantity: int
    price_ton: str
    status: OrderStatus
    created_at: datetime | None


class CreateOrderRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    service_id: int
    recipient: str
    quantity: int | None = None
