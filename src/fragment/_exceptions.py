from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any

import httpx


class FragmentError(Exception):
    """Base exception for all Fragment SDK errors."""

    status_code: int | None
    request: httpx.Request | None
    response: httpx.Response | None

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        request: httpx.Request | None = None,
        response: httpx.Response | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.request = request
        self.response = response

    def __str__(self) -> str:
        return self.message


class APIError(FragmentError):
    """HTTP error returned by the Fragment API."""

    status_code: int
    response: httpx.Response
    request: httpx.Request

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        response: httpx.Response,
        request: httpx.Request,
    ) -> None:
        super().__init__(
            message,
            status_code=status_code,
            response=response,
            request=request,
        )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(message={self.message!r}, status_code={self.status_code})"
        )


class BadRequestError(APIError):
    """400 Bad Request."""


class AuthenticationError(APIError):
    """401 Unauthenticated."""


class PermissionDeniedError(APIError):
    """403 Forbidden."""


class NotFoundError(APIError):
    """404 Not Found."""


class ConflictError(APIError):
    """409 Conflict."""


class UnprocessableEntityError(APIError):
    """422 Unprocessable Entity."""

    errors: dict[str, Any]

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        response: httpx.Response,
        request: httpx.Request,
        errors: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, status_code=status_code, response=response, request=request)
        self.errors = errors or {}


class RateLimitError(APIError):
    """429 Too Many Requests."""

    retry_after: float | None

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        response: httpx.Response,
        request: httpx.Request,
        retry_after: float | None = None,
    ) -> None:
        super().__init__(message, status_code=status_code, response=response, request=request)
        self.retry_after = retry_after


class InternalServerError(APIError):
    """5xx Server Error."""


class APIConnectionError(FragmentError):
    """Network connectivity error."""

    def __init__(self, *, message: str = "Connection error.", request: httpx.Request) -> None:
        super().__init__(message, request=request)


class APITimeoutError(FragmentError):
    """Request timed out."""

    def __init__(self, *, request: httpx.Request) -> None:
        super().__init__("Request timed out.", request=request)


_STATUS_CODE_MAP: dict[int, type[APIError]] = {
    400: BadRequestError,
    401: AuthenticationError,
    403: PermissionDeniedError,
    404: NotFoundError,
    409: ConflictError,
    422: UnprocessableEntityError,
    429: RateLimitError,
}


def _parse_retry_after(value: str | None) -> float | None:
    """Parse Retry-After header seconds or HTTP-date."""
    if value is None:
        return None

    stripped_value = value.strip()
    if not stripped_value:
        return None

    try:
        return max(0.0, float(stripped_value))
    except ValueError:
        try:
            retry_at = parsedate_to_datetime(stripped_value)
        except (TypeError, ValueError, IndexError, OverflowError):
            return None

        if retry_at.tzinfo is None:
            retry_at = retry_at.replace(tzinfo=timezone.utc)

        return max(0.0, (retry_at - datetime.now(timezone.utc)).total_seconds())


def _make_api_error(response: httpx.Response) -> APIError:
    """Build the appropriate APIError subclass from an HTTP response."""
    status = response.status_code
    try:
        body = response.json()
    except Exception:
        body = {}

    message = body.get("message", response.reason_phrase or "Unknown error")

    if status in _STATUS_CODE_MAP:
        exc_cls = _STATUS_CODE_MAP[status]
        kwargs: dict[str, Any] = {
            "message": message,
            "status_code": status,
            "response": response,
            "request": response.request,
        }
        if exc_cls is UnprocessableEntityError:
            kwargs["errors"] = body.get("errors", {})
        if exc_cls is RateLimitError:
            kwargs["retry_after"] = _parse_retry_after(response.headers.get("retry-after"))
        return exc_cls(**kwargs)

    if status >= 500:
        return InternalServerError(
            message,
            status_code=status,
            response=response,
            request=response.request,
        )

    return APIError(
        message,
        status_code=status,
        response=response,
        request=response.request,
    )
