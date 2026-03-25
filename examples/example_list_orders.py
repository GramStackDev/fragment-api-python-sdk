from __future__ import annotations

from fragment import FragmentClient, FragmentError


def main() -> None:
    """List and print orders with pagination."""
    with FragmentClient() as client:
        result = client.orders.list(page=1, per_page=10)

        print(f"Total orders: {result.meta.total}")
        print(f"Page: {result.meta.current_page}/{result.meta.last_page}")

        for order in result.data:
            print(
                f"- {order.id} | status={order.status} | recipient={order.recipient} | "
                f"quantity={order.quantity} | price_ton={order.price_ton}"
            )


if __name__ == "__main__":
    try:
        main()
    except FragmentError as exc:
        print(f"Failed to list orders: {exc}")
