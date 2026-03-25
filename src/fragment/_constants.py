from __future__ import annotations

import httpx

DEFAULT_BASE_URL = "https://gramstack.dev/api/v1"
DEFAULT_TIMEOUT = httpx.Timeout(timeout=30.0, connect=5.0)
DEFAULT_MAX_RETRIES = 3

INITIAL_RETRY_DELAY = 0.5
MAX_RETRY_DELAY = 8.0
