from __future__ import annotations

import os
import platform
import random
import time
from typing import Any, TypeVar

import httpx

from fragment._constants import (
    DEFAULT_BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
    INITIAL_RETRY_DELAY,
    MAX_RETRY_DELAY,
)
from fragment._exceptions import (
    APIConnectionError,
    APITimeoutError,
    FragmentError,
    _make_api_error,
    _parse_retry_after,
)
from fragment._version import __version__

_T = TypeVar("_T")

_RETRYABLE_STATUS_CODES = frozenset({429, 503})


def _default_headers(api_key: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "User-Agent": f"fragment-python-sdk/{__version__} python/{platform.python_version()}",
    }


def _calculate_retry_delay(attempt: int, retry_after: float | None) -> float:
    if retry_after is not None and retry_after > 0:
        return retry_after
    delay = min(INITIAL_RETRY_DELAY * (2**attempt), MAX_RETRY_DELAY)
    jitter = random.random() * 0.5 * delay  # noqa: S311
    return float(delay + jitter)


def _resolve_api_key(api_key: str | None) -> str:
    key = api_key or os.environ.get("FRAGMENT_API_KEY")
    if not key:
        raise FragmentError(
            "API key is required. Pass api_key= or set the FRAGMENT_API_KEY env variable."
        )
    return key


def _resolve_base_url(base_url: str | None) -> str:
    return base_url or os.environ.get("FRAGMENT_BASE_URL", DEFAULT_BASE_URL)


class SyncAPIClient:
    """Synchronous HTTP transport layer for the Fragment API."""

    _client: httpx.Client
    _owns_client: bool
    _max_retries: int

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: httpx.Timeout | float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        http_client: httpx.Client | None = None,
    ) -> None:
        resolved_key = _resolve_api_key(api_key)
        resolved_url = _resolve_base_url(base_url)
        if max_retries < 0:
            raise ValueError("max_retries must be greater than or equal to 0.")
        self._max_retries = max_retries

        if isinstance(timeout, (int, float)):
            timeout = httpx.Timeout(timeout=float(timeout), connect=5.0)

        if http_client is not None:
            self._client = http_client
            self._owns_client = False
        else:
            self._client = httpx.Client(
                base_url=resolved_url,
                headers=_default_headers(resolved_key),
                timeout=timeout,
            )
            self._owns_client = True

    def _build_request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> httpx.Request:
        return self._client.build_request(method, path, params=params, json=json)

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> httpx.Response:
        return self._retry_request(method, path, params=params, json=json)

    def _retry_request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> httpx.Response:
        last_exc: Exception | None = None

        for attempt in range(self._max_retries + 1):
            try:
                response = self._client.request(method, path, params=params, json=json)
            except httpx.TimeoutException as exc:
                last_exc = exc
                if attempt >= self._max_retries:
                    raise APITimeoutError(
                        request=exc.request if hasattr(exc, "request") else self._build_request(
                            method,
                            path,
                            params=params,
                            json=json,
                        ),
                    ) from exc
                time.sleep(_calculate_retry_delay(attempt, None))
                continue
            except httpx.NetworkError as exc:
                last_exc = exc
                if attempt >= self._max_retries:
                    raise APIConnectionError(
                        request=exc.request if hasattr(exc, "request") else self._build_request(
                            method,
                            path,
                            params=params,
                            json=json,
                        ),
                    ) from exc
                time.sleep(_calculate_retry_delay(attempt, None))
                continue

            if response.status_code in _RETRYABLE_STATUS_CODES and attempt < self._max_retries:
                retry_after = _parse_retry_after(response.headers.get("retry-after"))
                response.close()
                time.sleep(_calculate_retry_delay(attempt, retry_after))
                continue

            if response.status_code >= 400:
                raise _make_api_error(response)

            return response

        assert last_exc is not None  # noqa: S101
        raise last_exc

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> SyncAPIClient:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()


class AsyncAPIClient:
    """Asynchronous HTTP transport layer for the Fragment API."""

    _client: httpx.AsyncClient
    _owns_client: bool
    _max_retries: int

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: httpx.Timeout | float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        resolved_key = _resolve_api_key(api_key)
        resolved_url = _resolve_base_url(base_url)
        if max_retries < 0:
            raise ValueError("max_retries must be greater than or equal to 0.")
        self._max_retries = max_retries

        if isinstance(timeout, (int, float)):
            timeout = httpx.Timeout(timeout=float(timeout), connect=5.0)

        if http_client is not None:
            self._client = http_client
            self._owns_client = False
        else:
            self._client = httpx.AsyncClient(
                base_url=resolved_url,
                headers=_default_headers(resolved_key),
                timeout=timeout,
            )
            self._owns_client = True

    def _build_request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> httpx.Request:
        return self._client.build_request(method, path, params=params, json=json)

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> httpx.Response:
        return await self._retry_request(method, path, params=params, json=json)

    async def _retry_request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> httpx.Response:
        import asyncio

        last_exc: Exception | None = None

        for attempt in range(self._max_retries + 1):
            try:
                response = await self._client.request(method, path, params=params, json=json)
            except httpx.TimeoutException as exc:
                last_exc = exc
                if attempt >= self._max_retries:
                    raise APITimeoutError(
                        request=exc.request if hasattr(exc, "request") else self._build_request(
                            method,
                            path,
                            params=params,
                            json=json,
                        ),
                    ) from exc
                await asyncio.sleep(_calculate_retry_delay(attempt, None))
                continue
            except httpx.NetworkError as exc:
                last_exc = exc
                if attempt >= self._max_retries:
                    raise APIConnectionError(
                        request=exc.request if hasattr(exc, "request") else self._build_request(
                            method,
                            path,
                            params=params,
                            json=json,
                        ),
                    ) from exc
                await asyncio.sleep(_calculate_retry_delay(attempt, None))
                continue

            if response.status_code in _RETRYABLE_STATUS_CODES and attempt < self._max_retries:
                retry_after = _parse_retry_after(response.headers.get("retry-after"))
                await response.aclose()
                await asyncio.sleep(_calculate_retry_delay(attempt, retry_after))
                continue

            if response.status_code >= 400:
                raise _make_api_error(response)

            return response

        assert last_exc is not None  # noqa: S101
        raise last_exc

    async def close(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> AsyncAPIClient:
        return self

    async def __aexit__(self, *_args: object) -> None:
        await self.close()
