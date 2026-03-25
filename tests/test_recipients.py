from __future__ import annotations

import httpx
import pytest
import respx

from fragment import AsyncFragmentClient, FragmentClient, FragmentUser

BASE_URL = "https://test.api/api/v1"

RECIPIENT_RESPONSE = {
    "data": {
        "name": "Pavel Durov",
        "recipient": "@durov",
        "photo": "https://example.com/photo.jpg",
    }
}

RECIPIENT_NULL_RESPONSE = {"data": None}


class TestSyncRecipients:
    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        self.client = FragmentClient(api_key="test", base_url=BASE_URL, max_retries=0)

    def test_lookup_found(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("/recipients").mock(
            return_value=httpx.Response(200, json=RECIPIENT_RESPONSE)
        )
        user = self.client.recipients.lookup(service="premium", recipient="@durov")

        assert user is not None
        assert isinstance(user, FragmentUser)
        assert user.name == "Pavel Durov"
        assert user.recipient == "@durov"
        assert user.photo == "https://example.com/photo.jpg"

    def test_lookup_not_found(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("/recipients").mock(
            return_value=httpx.Response(200, json=RECIPIENT_NULL_RESPONSE)
        )
        user = self.client.recipients.lookup(service="stars", recipient="@nobody")

        assert user is None

    def test_lookup_sends_params(self, respx_mock: respx.MockRouter) -> None:
        route = respx_mock.get("/recipients").mock(
            return_value=httpx.Response(200, json=RECIPIENT_RESPONSE)
        )
        self.client.recipients.lookup(service="premium", recipient="@durov")

        request = route.calls[0].request
        assert b"service=premium" in request.url.raw_path
        assert b"recipient=%40durov" in request.url.raw_path


class TestAsyncRecipients:
    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        self.client = AsyncFragmentClient(api_key="test", base_url=BASE_URL, max_retries=0)

    @pytest.mark.asyncio
    async def test_lookup_found(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("/recipients").mock(
            return_value=httpx.Response(200, json=RECIPIENT_RESPONSE)
        )
        user = await self.client.recipients.lookup(service="premium", recipient="@durov")

        assert user is not None
        assert user.name == "Pavel Durov"

    @pytest.mark.asyncio
    async def test_lookup_null(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("/recipients").mock(
            return_value=httpx.Response(200, json=RECIPIENT_NULL_RESPONSE)
        )
        user = await self.client.recipients.lookup(service="stars", recipient="@nobody")

        assert user is None
