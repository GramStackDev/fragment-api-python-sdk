from __future__ import annotations

import httpx
import pytest
import respx

from fragment import (
    AsyncFragmentClient,
    FragmentClient,
    NotFoundError,
    Order,
    OrderListResponse,
    OrderStatus,
)

BASE_URL = "https://test.api/api/v1"

ORDER_DATA = {
    "id": "2d0c6ef1-4f4f-4f44-9b4d-8d1dcf7d6b60",
    "service_id": 1,
    "service_name": "Telegram Premium 3 months",
    "recipient": "@durov",
    "quantity": 1,
    "price_ton": "5.25",
    "status": "completed",
    "created_at": "2025-01-15T12:00:00Z",
}

ORDERS_LIST_RESPONSE = {
    "data": [ORDER_DATA],
    "links": {
        "first": "https://api.test/api/v1/orders?page=1",
        "last": "https://api.test/api/v1/orders?page=1",
        "prev": None,
        "next": None,
    },
    "meta": {
        "current_page": 1,
        "from": 1,
        "last_page": 1,
        "path": "https://api.test/api/v1/orders",
        "per_page": 15,
        "to": 1,
        "total": 1,
    },
}


class TestSyncOrders:
    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        self.client = FragmentClient(api_key="test", base_url=BASE_URL, max_retries=0)

    def test_list(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("/orders").mock(return_value=httpx.Response(200, json=ORDERS_LIST_RESPONSE))
        result = self.client.orders.list()

        assert isinstance(result, OrderListResponse)
        assert len(result.data) == 1
        assert result.meta.total == 1
        assert result.meta.current_page == 1
        assert result.links.first is not None

    def test_list_with_pagination(self, respx_mock: respx.MockRouter) -> None:
        route = respx_mock.get("/orders").mock(
            return_value=httpx.Response(200, json=ORDERS_LIST_RESPONSE)
        )
        self.client.orders.list(page=2, per_page=10)

        assert route.called
        request = route.calls[0].request
        assert b"page=2" in request.url.raw_path
        assert b"per_page=10" in request.url.raw_path

    def test_create(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.post("/orders").mock(
            return_value=httpx.Response(200, json={"data": ORDER_DATA})
        )
        order = self.client.orders.create(
            service_id=1,
            recipient="@durov",
            quantity=1,
        )

        assert isinstance(order, Order)
        assert order.id == "2d0c6ef1-4f4f-4f44-9b4d-8d1dcf7d6b60"
        assert order.service_id == 1
        assert order.recipient == "@durov"
        assert order.status == OrderStatus.COMPLETED
        assert order.price_ton == "5.25"

    def test_create_without_quantity(self, respx_mock: respx.MockRouter) -> None:
        route = respx_mock.post("/orders").mock(
            return_value=httpx.Response(200, json={"data": ORDER_DATA})
        )
        self.client.orders.create(service_id=1, recipient="@durov")

        body = route.calls[0].request.content
        assert b"quantity" not in body

    def test_retrieve(self, respx_mock: respx.MockRouter) -> None:
        order_id = "2d0c6ef1-4f4f-4f44-9b4d-8d1dcf7d6b60"
        respx_mock.get(f"/orders/{order_id}").mock(
            return_value=httpx.Response(200, json={"data": ORDER_DATA})
        )
        order = self.client.orders.retrieve(order_id)

        assert isinstance(order, Order)
        assert order.id == order_id

    def test_retrieve_not_found(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("/orders/nonexistent").mock(
            return_value=httpx.Response(404, json={"message": "Not found"})
        )
        with pytest.raises(NotFoundError):
            self.client.orders.retrieve("nonexistent")


class TestAsyncOrders:
    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        self.client = AsyncFragmentClient(api_key="test", base_url=BASE_URL, max_retries=0)

    @pytest.mark.asyncio
    async def test_list(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("/orders").mock(return_value=httpx.Response(200, json=ORDERS_LIST_RESPONSE))
        result = await self.client.orders.list()

        assert isinstance(result, OrderListResponse)
        assert len(result.data) == 1

    @pytest.mark.asyncio
    async def test_create(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.post("/orders").mock(
            return_value=httpx.Response(200, json={"data": ORDER_DATA})
        )
        order = await self.client.orders.create(service_id=1, recipient="@durov")

        assert isinstance(order, Order)
        assert order.recipient == "@durov"

    @pytest.mark.asyncio
    async def test_retrieve(self, respx_mock: respx.MockRouter) -> None:
        order_id = "2d0c6ef1-4f4f-4f44-9b4d-8d1dcf7d6b60"
        respx_mock.get(f"/orders/{order_id}").mock(
            return_value=httpx.Response(200, json={"data": ORDER_DATA})
        )
        order = await self.client.orders.retrieve(order_id)

        assert order.id == order_id
