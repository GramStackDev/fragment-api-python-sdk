from __future__ import annotations

from fragment import FragmentClient, FragmentError


def main() -> None:
    """Fetch and print current account balance."""
    # Uses FRAGMENT_API_KEY from environment by default.
    with FragmentClient() as client:
        balance = client.balance.retrieve()
        print(f"Balance: {balance.balance.amount} {balance.balance.currency}")


if __name__ == "__main__":
    try:
        main()
    except FragmentError as exc:
        print(f"Failed to fetch balance: {exc}")
