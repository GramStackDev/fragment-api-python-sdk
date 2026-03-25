from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from fragment.types.order import Order


class PaginationLinks(BaseModel):
    model_config = ConfigDict(frozen=True)

    first: str | None
    last: str | None
    prev: str | None
    next: str | None


class PaginationMeta(BaseModel):
    model_config = ConfigDict(frozen=True)

    current_page: int
    from_: int | None = Field(alias="from")
    last_page: int
    path: str | None
    per_page: int
    to: int | None
    total: int


class OrderListResponse(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    data: list[Order]
    links: PaginationLinks
    meta: PaginationMeta
