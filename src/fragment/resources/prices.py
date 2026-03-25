from __future__ import annotations

from typing import TYPE_CHECKING

from fragment.types.price import Price

if TYPE_CHECKING:
    from fragment._base_client import AsyncAPIClient, SyncAPIClient


class SyncPrices:
    """Synchronous prices resource."""

    def __init__(self, client: SyncAPIClient) -> None:
        self._client = client

    def list(self) -> list[Price]:
        """List all available services and their prices."""
        response = self._client._request("GET", "/prices")
        data = response.json()["data"]
        return [Price.model_validate(item) for item in data]


class AsyncPrices:
    """Asynchronous prices resource."""

    def __init__(self, client: AsyncAPIClient) -> None:
        self._client = client

    async def list(self) -> list[Price]:
        """List all available services and their prices."""
        response = await self._client._request("GET", "/prices")
        data = response.json()["data"]
        return [Price.model_validate(item) for item in data]
