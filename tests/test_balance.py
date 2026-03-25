from __future__ import annotations

import httpx
import pytest
import respx

from fragment import AsyncFragmentClient, Balance, FragmentClient, Money

BASE_URL = "https://test.api/api/v1"

BALANCE_RESPONSE = {
    "data": {
        "balance": {
            "amount": "123.456",
            "currency": "TON",
        }
    }
}


class TestSyncBalance:
    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        self.client = FragmentClient(api_key="test", base_url=BASE_URL, max_retries=0)

    def test_retrieve(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("/balance").mock(return_value=httpx.Response(200, json=BALANCE_RESPONSE))
        balance = self.client.balance.retrieve()

        assert isinstance(balance, Balance)
        assert isinstance(balance.balance, Money)
        assert balance.balance.amount == "123.456"
        assert balance.balance.currency == "TON"


class TestAsyncBalance:
    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        self.client = AsyncFragmentClient(api_key="test", base_url=BASE_URL, max_retries=0)

    @pytest.mark.asyncio
    async def test_retrieve(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("/balance").mock(return_value=httpx.Response(200, json=BALANCE_RESPONSE))
        balance = await self.client.balance.retrieve()

        assert isinstance(balance, Balance)
        assert balance.balance.amount == "123.456"
        assert balance.balance.currency == "TON"
