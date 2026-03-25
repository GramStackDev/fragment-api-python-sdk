from __future__ import annotations

from typing import TYPE_CHECKING

from fragment.types.order import CreateOrderRequest, Order
from fragment.types.pagination import OrderListResponse

if TYPE_CHECKING:
    from fragment._base_client import AsyncAPIClient, SyncAPIClient


class SyncOrders:
    """Synchronous orders resource."""

    def __init__(self, client: SyncAPIClient) -> None:
        self._client = client

    def list(
        self,
        *,
        page: int | None = None,
        per_page: int | None = None,
    ) -> OrderListResponse:
        """List orders with pagination."""
        params: dict[str, int] = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        response = self._client._request("GET", "/orders", params=params)
        return OrderListResponse.model_validate(response.json())

    def create(
        self,
        *,
        service_id: int,
        recipient: str,
        quantity: int | None = None,
    ) -> Order:
        """Create a new order."""
        body = CreateOrderRequest(
            service_id=service_id,
            recipient=recipient,
            quantity=quantity,
        )
        response = self._client._request(
            "POST", "/orders", json=body.model_dump(exclude_none=True)
        )
        return Order.model_validate(response.json()["data"])

    def retrieve(self, order_id: str) -> Order:
        """Retrieve an order by its UUID."""
        response = self._client._request("GET", f"/orders/{order_id}")
        return Order.model_validate(response.json()["data"])


class AsyncOrders:
    """Asynchronous orders resource."""

    def __init__(self, client: AsyncAPIClient) -> None:
        self._client = client

    async def list(
        self,
        *,
        page: int | None = None,
        per_page: int | None = None,
    ) -> OrderListResponse:
        """List orders with pagination."""
        params: dict[str, int] = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        response = await self._client._request("GET", "/orders", params=params)
        return OrderListResponse.model_validate(response.json())

    async def create(
        self,
        *,
        service_id: int,
        recipient: str,
        quantity: int | None = None,
    ) -> Order:
        """Create a new order."""
        body = CreateOrderRequest(
            service_id=service_id,
            recipient=recipient,
            quantity=quantity,
        )
        response = await self._client._request(
            "POST", "/orders", json=body.model_dump(exclude_none=True)
        )
        return Order.model_validate(response.json()["data"])

    async def retrieve(self, order_id: str) -> Order:
        """Retrieve an order by its UUID."""
        response = await self._client._request("GET", f"/orders/{order_id}")
        return Order.model_validate(response.json()["data"])
