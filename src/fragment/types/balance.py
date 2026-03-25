from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Money(BaseModel):
    model_config = ConfigDict(frozen=True)

    amount: str
    currency: str


class Balance(BaseModel):
    model_config = ConfigDict(frozen=True)

    balance: Money
