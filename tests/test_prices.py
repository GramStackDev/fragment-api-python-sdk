from __future__ import annotations

import httpx
import pytest
import respx

from fragment import AsyncFragmentClient, FragmentClient, Price

BASE_URL = "https://test.api/api/v1"

PRICES_RESPONSE = {
    "data": [
        {
            "service_id": "1",
            "service_name": "Telegram Premium 3 months",
            "price_in_usd": 11.99,
            "price_in_ton": 5.25,
        },
        {
            "service_id": "2",
            "service_name": "Telegram Stars 100",
            "price_in_usd": 1.99,
            "price_in_ton": 0.88,
        },
    ]
}


class TestSyncPrices:
    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        self.client = FragmentClient(api_key="test", base_url=BASE_URL, max_retries=0)

    def test_list(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("/prices").mock(return_value=httpx.Response(200, json=PRICES_RESPONSE))
        prices = self.client.prices.list()

        assert len(prices) == 2
        assert all(isinstance(p, Price) for p in prices)
        assert prices[0].service_id == "1"
        assert prices[0].service_name == "Telegram Premium 3 months"
        assert prices[0].price_in_usd == 11.99
        assert prices[0].price_in_ton == 5.25
        assert prices[1].service_id == "2"


class TestAsyncPrices:
    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        self.client = AsyncFragmentClient(api_key="test", base_url=BASE_URL, max_retries=0)

    @pytest.mark.asyncio
    async def test_list(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("/prices").mock(return_value=httpx.Response(200, json=PRICES_RESPONSE))
        prices = await self.client.prices.list()

        assert len(prices) == 2
        assert all(isinstance(p, Price) for p in prices)
