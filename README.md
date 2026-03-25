# Fragment Python SDK

Official Python client for the [GramStack - Fragment Rest API](https://gramstack.dev)

Provides both **synchronous** and **asynchronous** clients with full type annotations, automatic retries, and Pydantic v2 models.
Requires Python 3.9+

## Installation

```bash
# pip
pip install fragment-sdk

# uv
uv add fragment-sdk
```

## Quick Start

```python
from fragment import FragmentClient

client = FragmentClient(api_key="your-api-key")

balance = client.balance.retrieve()
print(f"Balance: {balance.balance.amount} {balance.balance.currency}")
```

## Configuration

### API Key

The API key can be provided directly or via environment variable:

```python
# Option 1: pass directly
client = FragmentClient(api_key="your-api-key")

# Option 2: set FRAGMENT_API_KEY env variable
# export FRAGMENT_API_KEY=your-api-key
client = FragmentClient()
```

### Base URL

```python
# Custom base URL
client = FragmentClient(
    api_key="your-api-key",
    base_url="https://gramstack.dev/api/v1",
)

# Or via env: FRAGMENT_BASE_URL
```

### Advanced Options

```python
import httpx
from fragment import FragmentClient

client = FragmentClient(
    api_key="your-api-key",
    timeout=60.0,           # request timeout in seconds (default: 30)
    max_retries=5,          # retry count for 429/503/timeouts (default: 3)
    http_client=httpx.Client(  # bring your own httpx client
        base_url="https://gramstack.dev/api/v1",
        headers={"Authorization": "Bearer your-api-key"},
    ),
)
```

## Usage

### Synchronous

```python
from fragment import FragmentClient

with FragmentClient(api_key="your-api-key") as client:
    # Balance
    balance = client.balance.retrieve()
    print(balance.balance.amount)

    # Prices
    prices = client.prices.list()
    for price in prices:
        print(f"{price.service_name}: {price.price_in_ton} TON")

    # Create an order
    order = client.orders.create(
        service_id=1,
        recipient="@example_nickname",
        quantity=1,
    )
    print(f"Order {order.id}: {order.status}")

    # List orders with pagination
    result = client.orders.list(page=1, per_page=10)
    for order in result.data:
        print(f"{order.id} — {order.status}")
    print(f"Total: {result.meta.total}")

    # Retrieve a single order
    order = client.orders.retrieve("order-uuid")

    # Look up a recipient
    user = client.recipients.lookup(service="premium", recipient="@example_nickname")
    if user:
        print(f"Found: {user.name}")
```

### Asynchronous

```python
import asyncio
from fragment import AsyncFragmentClient

async def main():
    async with AsyncFragmentClient(api_key="your-api-key") as client:
        balance = await client.balance.retrieve()
        print(balance.balance.amount)

        prices = await client.prices.list()
        for price in prices:
            print(f"{price.service_name}: {price.price_in_ton} TON")

        order = await client.orders.create(
            service_id=1,
            recipient="@example_nickname",
        )
        print(f"Order {order.id}: {order.status}")

asyncio.run(main())
```

## Error Handling

All exceptions inherit from `FragmentError`:

```python
from fragment import (
    FragmentClient,
    FragmentError,
    AuthenticationError,
    ConflictError,
    NotFoundError,
    RateLimitError,
)

client = FragmentClient(api_key="your-api-key")

try:
    order = client.orders.retrieve("some-uuid")
except AuthenticationError:
    print("Invalid API key")
except ConflictError:
    print("Order already exists")
except NotFoundError:
    print("Order not found")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after}s")
except FragmentError as e:
    print(f"API error: {e.message}")
```

### Exception Hierarchy

| Exception                  | HTTP Status | Description           |
|----------------------------|-------------|-----------------------|
| `BadRequestError`          | 400         | Invalid request       |
| `AuthenticationError`      | 401         | Invalid/missing key   |
| `PermissionDeniedError`    | 403         | Forbidden             |
| `NotFoundError`            | 404         | Resource not found    |
| `ConflictError`            | 409         | Resource conflict     |
| `UnprocessableEntityError` | 422         | Validation failed     |
| `RateLimitError`           | 429         | Too many requests     |
| `InternalServerError`      | 5xx         | Server error          |
| `APITimeoutError`          | —           | Request timed out     |
| `APIConnectionError`       | —           | Network error         |

## Resources API

| Resource     | Method                                            | Returns                  |
|--------------|---------------------------------------------------|--------------------------|
| `balance`    | `retrieve()`                                      | `Balance`                |
| `orders`     | `list(*, page=, per_page=)`                       | `OrderListResponse`      |
| `orders`     | `create(*, service_id=, recipient=, quantity=)`    | `Order`                  |
| `orders`     | `retrieve(order_id)`                               | `Order`                  |
| `prices`     | `list()`                                          | `list[Price]`            |
| `recipients` | `lookup(*, service=, recipient=)`                  | `FragmentUser \| None`   |

## Retries

The client automatically retries on:

- **429** Too Many Requests (respects `Retry-After` header)
- **503** Service Unavailable
- Timeouts and connection errors

Retry uses exponential backoff with jitter. Configure with `max_retries=` (default: 3).

## Contributing

```bash
# Clone and install
git clone https://github.com/GramStackDev/fragment-api-python-sdk.git
cd fragment-api-python-sdk
uv sync --extra dev

# Run tests
uv run pytest

# Lint & format
uv run ruff check src/ tests/
uv run ruff format src/ tests/

# Type check
uv run mypy

# Build distributions
uv build
```

## License

MIT
