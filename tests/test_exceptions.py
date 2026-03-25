from __future__ import annotations

from datetime import datetime, timedelta, timezone

import httpx
import pytest
import respx

from fragment import (
    AsyncFragmentClient,
    AuthenticationError,
    BadRequestError,
    ConflictError,
    FragmentClient,
    InternalServerError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    UnprocessableEntityError,
)
from fragment._exceptions import APIError

BASE_URL = "https://test.api/api/v1"


class TestSyncExceptionMapping:
    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        self.client = FragmentClient(api_key="test", base_url=BASE_URL, max_retries=0)

    def test_400_bad_request(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("/balance").mock(
            return_value=httpx.Response(400, json={"message": "Bad request"})
        )
        with pytest.raises(BadRequestError) as exc_info:
            self.client.balance.retrieve()
        assert exc_info.value.status_code == 400
        assert exc_info.value.message == "Bad request"

    def test_401_authentication(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("/balance").mock(
            return_value=httpx.Response(401, json={"message": "Unauthenticated"})
        )
        with pytest.raises(AuthenticationError) as exc_info:
            self.client.balance.retrieve()
        assert exc_info.value.status_code == 401

    def test_403_permission_denied(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("/orders/some-uuid").mock(
            return_value=httpx.Response(403, json={"message": "Forbidden"})
        )
        with pytest.raises(PermissionDeniedError) as exc_info:
            self.client.orders.retrieve("some-uuid")
        assert exc_info.value.status_code == 403

    def test_404_not_found(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("/orders/missing").mock(
            return_value=httpx.Response(404, json={"message": "Not found"})
        )
        with pytest.raises(NotFoundError) as exc_info:
            self.client.orders.retrieve("missing")
        assert exc_info.value.status_code == 404
        assert exc_info.value.message == "Not found"

    def test_409_conflict(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.post("/orders").mock(
            return_value=httpx.Response(409, json={"message": "Order already exists"})
        )
        with pytest.raises(ConflictError) as exc_info:
            self.client.orders.create(service_id=1, recipient="@durov")
        assert exc_info.value.status_code == 409
        assert exc_info.value.message == "Order already exists"

    def test_422_unprocessable(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.post("/orders").mock(
            return_value=httpx.Response(
                422,
                json={
                    "message": "Validation failed",
                    "errors": {"recipient": ["Required field"]},
                },
            )
        )
        with pytest.raises(UnprocessableEntityError) as exc_info:
            self.client.orders.create(service_id=1, recipient="")
        assert exc_info.value.status_code == 422
        assert exc_info.value.errors == {"recipient": ["Required field"]}

    def test_429_rate_limit(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("/balance").mock(
            return_value=httpx.Response(
                429,
                json={"message": "Too many requests"},
                headers={"retry-after": "30"},
            )
        )
        with pytest.raises(RateLimitError) as exc_info:
            self.client.balance.retrieve()
        assert exc_info.value.status_code == 429
        assert exc_info.value.retry_after == 30.0

    def test_429_rate_limit_no_retry_after(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("/balance").mock(
            return_value=httpx.Response(429, json={"message": "Too many requests"})
        )
        with pytest.raises(RateLimitError) as exc_info:
            self.client.balance.retrieve()
        assert exc_info.value.retry_after is None

    def test_429_rate_limit_http_date(self, respx_mock: respx.MockRouter) -> None:
        retry_after = (datetime.now(timezone.utc) + timedelta(seconds=30)).strftime(
            "%a, %d %b %Y %H:%M:%S GMT"
        )
        respx_mock.get("/balance").mock(
            return_value=httpx.Response(
                429,
                json={"message": "Too many requests"},
                headers={"retry-after": retry_after},
            )
        )
        with pytest.raises(RateLimitError) as exc_info:
            self.client.balance.retrieve()
        assert exc_info.value.retry_after is not None
        assert 0.0 <= exc_info.value.retry_after <= 30.0

    def test_500_internal_server_error(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("/balance").mock(
            return_value=httpx.Response(500, json={"message": "Internal server error"})
        )
        with pytest.raises(InternalServerError) as exc_info:
            self.client.balance.retrieve()
        assert exc_info.value.status_code == 500

    def test_502_maps_to_internal(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("/balance").mock(
            return_value=httpx.Response(502, json={"message": "Bad gateway"})
        )
        with pytest.raises(InternalServerError):
            self.client.balance.retrieve()

    def test_unknown_4xx(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("/balance").mock(
            return_value=httpx.Response(418, json={"message": "I'm a teapot"})
        )
        with pytest.raises(APIError) as exc_info:
            self.client.balance.retrieve()
        assert exc_info.value.status_code == 418

    def test_error_has_response_and_request(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("/balance").mock(
            return_value=httpx.Response(401, json={"message": "Unauthenticated"})
        )
        with pytest.raises(AuthenticationError) as exc_info:
            self.client.balance.retrieve()
        assert exc_info.value.response is not None
        assert exc_info.value.request is not None


class TestAsyncExceptionMapping:
    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        self.client = AsyncFragmentClient(api_key="test", base_url=BASE_URL, max_retries=0)

    @pytest.mark.asyncio
    async def test_401_async(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("/balance").mock(
            return_value=httpx.Response(401, json={"message": "Unauthenticated"})
        )
        with pytest.raises(AuthenticationError):
            await self.client.balance.retrieve()

    @pytest.mark.asyncio
    async def test_404_async(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("/orders/missing").mock(
            return_value=httpx.Response(404, json={"message": "Not found"})
        )
        with pytest.raises(NotFoundError):
            await self.client.orders.retrieve("missing")
