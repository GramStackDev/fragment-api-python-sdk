from __future__ import annotations

from typing import TYPE_CHECKING

from fragment.types.recipient import FragmentUser, ServiceType

if TYPE_CHECKING:
    from fragment._base_client import AsyncAPIClient, SyncAPIClient


class SyncRecipients:
    """Synchronous recipients resource."""

    def __init__(self, client: SyncAPIClient) -> None:
        self._client = client

    def lookup(
        self,
        *,
        service: ServiceType | str,
        recipient: str,
    ) -> FragmentUser | None:
        """Look up a Telegram user on Fragment.

        Returns None if the user is not found.
        """
        response = self._client._request(
            "GET",
            "/recipients",
            params={"service": str(service), "recipient": recipient},
        )
        data = response.json()["data"]
        if data is None:
            return None
        return FragmentUser.model_validate(data)


class AsyncRecipients:
    """Asynchronous recipients resource."""

    def __init__(self, client: AsyncAPIClient) -> None:
        self._client = client

    async def lookup(
        self,
        *,
        service: ServiceType | str,
        recipient: str,
    ) -> FragmentUser | None:
        """Look up a Telegram user on Fragment.

        Returns None if the user is not found.
        """
        response = await self._client._request(
            "GET",
            "/recipients",
            params={"service": str(service), "recipient": recipient},
        )
        data = response.json()["data"]
        if data is None:
            return None
        return FragmentUser.model_validate(data)
