from __future__ import annotations

import httpx

from fragment._base_client import AsyncAPIClient, SyncAPIClient
from fragment._constants import DEFAULT_MAX_RETRIES, DEFAULT_TIMEOUT
from fragment.resources.balance import AsyncBalance, SyncBalance
from fragment.resources.orders import AsyncOrders, SyncOrders
from fragment.resources.prices import AsyncPrices, SyncPrices
from fragment.resources.recipients import AsyncRecipients, SyncRecipients


class FragmentClient(SyncAPIClient):
    """Synchronous client for the Fragment API.

    Example::

        from fragment import FragmentClient

        client = FragmentClient(api_key="sk-...")
        balance = client.balance.retrieve()
        print(balance.balance.amount)
    """

    balance: SyncBalance
    orders: SyncOrders
    prices: SyncPrices
    recipients: SyncRecipients

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: httpx.Timeout | float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        http_client: httpx.Client | None = None,
    ) -> None:
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            http_client=http_client,
        )
        self.balance = SyncBalance(self)
        self.orders = SyncOrders(self)
        self.prices = SyncPrices(self)
        self.recipients = SyncRecipients(self)

    def __enter__(self) -> FragmentClient:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()


class AsyncFragmentClient(AsyncAPIClient):
    """Asynchronous client for the Fragment API.

    Example::

        import asyncio
        from fragment import AsyncFragmentClient

        async def main():
            async with AsyncFragmentClient(api_key="sk-...") as client:
                balance = await client.balance.retrieve()
                print(balance.balance.amount)

        asyncio.run(main())
    """

    balance: AsyncBalance
    orders: AsyncOrders
    prices: AsyncPrices
    recipients: AsyncRecipients

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: httpx.Timeout | float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            http_client=http_client,
        )
        self.balance = AsyncBalance(self)
        self.orders = AsyncOrders(self)
        self.prices = AsyncPrices(self)
        self.recipients = AsyncRecipients(self)

    async def __aenter__(self) -> AsyncFragmentClient:
        return self

    async def __aexit__(self, *_args: object) -> None:
        await self.close()
