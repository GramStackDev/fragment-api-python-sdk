from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Price(BaseModel):
    model_config = ConfigDict(frozen=True)

    service_id: str
    service_name: str
    price_in_usd: float
    price_in_ton: float
