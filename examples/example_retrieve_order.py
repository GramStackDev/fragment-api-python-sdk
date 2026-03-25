from __future__ import annotations

import os

from fragment import FragmentClient, FragmentError


def main() -> None:
    """Retrieve and print a single order by UUID.

    Set `FRAGMENT_ORDER_ID` in environment variables before running.
    """
    order_id = os.environ.get("FRAGMENT_ORDER_ID", "")
    if not order_id:
        raise SystemExit('Set "FRAGMENT_ORDER_ID" env var to an order UUID.')

    with FragmentClient() as client:
        order = client.orders.retrieve(order_id)
        print(f"Order: {order.id}")
        print(f"Status: {order.status}")
        print(f"Service: {order.service_name} (id={order.service_id})")
        print(f"Recipient: {order.recipient}")
        print(f"Quantity: {order.quantity}")
        print(f"Price TON: {order.price_ton}")
        if order.created_at is not None:
            print(f"Created at: {order.created_at.isoformat()}")


if __name__ == "__main__":
    try:
        main()
    except FragmentError as exc:
        print(f"Failed to retrieve order: {exc}")
