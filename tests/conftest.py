from __future__ import annotations

import pytest
import respx

from fragment import AsyncFragmentClient, FragmentClient

BASE_URL = "https://test.api/api/v1"
API_KEY = "test-key-123"


@pytest.fixture()
def sync_client() -> FragmentClient:
    return FragmentClient(api_key=API_KEY, base_url=BASE_URL, max_retries=0)


@pytest.fixture()
def async_client() -> AsyncFragmentClient:
    return AsyncFragmentClient(api_key=API_KEY, base_url=BASE_URL, max_retries=0)


@pytest.fixture()
def respx_mock() -> respx.MockRouter:  # type: ignore[type-arg]
    with respx.mock(base_url=BASE_URL, assert_all_called=True) as mock:
        yield mock
