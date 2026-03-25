from __future__ import annotations

import os
from unittest.mock import patch

import httpx
import pytest

from fragment import AsyncFragmentClient, FragmentClient, FragmentError
from fragment._version import __version__


class TestFragmentClientInit:
    def test_api_key_from_param(self) -> None:
        client = FragmentClient(api_key="sk-test")
        assert client._client.headers["authorization"] == "Bearer sk-test"
        client.close()

    def test_api_key_from_env(self) -> None:
        with patch.dict(os.environ, {"FRAGMENT_API_KEY": "sk-env"}):
            client = FragmentClient()
            assert client._client.headers["authorization"] == "Bearer sk-env"
            client.close()

    def test_missing_api_key_raises(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("FRAGMENT_API_KEY", None)
            with pytest.raises(FragmentError, match="API key is required"):
                FragmentClient()

    def test_base_url_from_param(self) -> None:
        client = FragmentClient(api_key="sk-test", base_url="https://custom.api/v1")
        assert str(client._client.base_url).rstrip("/") == "https://custom.api/v1"
        client.close()

    def test_base_url_from_env(self) -> None:
        with patch.dict(os.environ, {"FRAGMENT_BASE_URL": "https://env.api/v1"}):
            client = FragmentClient(api_key="sk-test")
            assert str(client._client.base_url).rstrip("/") == "https://env.api/v1"
            client.close()

    def test_custom_http_client(self) -> None:
        custom = httpx.Client(base_url="https://custom.test")
        client = FragmentClient(api_key="sk-test", http_client=custom)
        assert client._client is custom
        assert not client._owns_client
        client.close()
        custom.close()

    def test_context_manager(self) -> None:
        with FragmentClient(api_key="sk-test") as client:
            assert client.balance is not None
            assert client.orders is not None
            assert client.prices is not None
            assert client.recipients is not None

    def test_default_user_agent(self) -> None:
        client = FragmentClient(api_key="sk-test")
        user_agent = client._client.headers["user-agent"]
        assert user_agent.startswith(f"fragment-python-sdk/{__version__}")
        client.close()

    def test_negative_max_retries_raises(self) -> None:
        with pytest.raises(ValueError, match="max_retries"):
            FragmentClient(api_key="sk-test", max_retries=-1)

    def test_resources_are_attached(self) -> None:
        client = FragmentClient(api_key="sk-test")
        from fragment.resources.balance import SyncBalance
        from fragment.resources.orders import SyncOrders
        from fragment.resources.prices import SyncPrices
        from fragment.resources.recipients import SyncRecipients

        assert isinstance(client.balance, SyncBalance)
        assert isinstance(client.orders, SyncOrders)
        assert isinstance(client.prices, SyncPrices)
        assert isinstance(client.recipients, SyncRecipients)
        client.close()


class TestAsyncFragmentClientInit:
    @pytest.mark.asyncio
    async def test_api_key_from_param(self) -> None:
        client = AsyncFragmentClient(api_key="sk-test")
        assert client._client.headers["authorization"] == "Bearer sk-test"
        await client.close()

    @pytest.mark.asyncio
    async def test_async_context_manager(self) -> None:
        async with AsyncFragmentClient(api_key="sk-test") as client:
            assert client.balance is not None

    @pytest.mark.asyncio
    async def test_resources_are_attached(self) -> None:
        client = AsyncFragmentClient(api_key="sk-test")
        from fragment.resources.balance import AsyncBalance
        from fragment.resources.orders import AsyncOrders
        from fragment.resources.prices import AsyncPrices
        from fragment.resources.recipients import AsyncRecipients

        assert isinstance(client.balance, AsyncBalance)
        assert isinstance(client.orders, AsyncOrders)
        assert isinstance(client.prices, AsyncPrices)
        assert isinstance(client.recipients, AsyncRecipients)
        await client.close()
