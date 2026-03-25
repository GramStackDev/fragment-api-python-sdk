from __future__ import annotations

from typing import TYPE_CHECKING

from fragment.types.balance import Balance

if TYPE_CHECKING:
    from fragment._base_client import AsyncAPIClient, SyncAPIClient


class SyncBalance:
    """Synchronous balance resource."""

    def __init__(self, client: SyncAPIClient) -> None:
        self._client = client

    def retrieve(self) -> Balance:
        """Get the current account balance."""
        response = self._client._request("GET", "/balance")
        return Balance.model_validate(response.json()["data"])


class AsyncBalance:
    """Asynchronous balance resource."""

    def __init__(self, client: AsyncAPIClient) -> None:
        self._client = client

    async def retrieve(self) -> Balance:
        """Get the current account balance."""
        response = await self._client._request("GET", "/balance")
        return Balance.model_validate(response.json()["data"])
