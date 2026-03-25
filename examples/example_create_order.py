from __future__ import annotations

from fragment import FragmentClient, FragmentError


def main() -> None:
    """Create an example order via the Fragment SDK."""
    with FragmentClient(api_key="your-api-key") as client:
        order = client.orders.create(
            service_id=4,
            recipient="@example_nickname",
            quantity=50,
        )
        print(f"Created order: {order.id}")
        print(f"Status: {order.status}")


if __name__ == "__main__":
    try:
        main()
    except FragmentError as exc:
        print(f"Failed to create order: {exc}")
