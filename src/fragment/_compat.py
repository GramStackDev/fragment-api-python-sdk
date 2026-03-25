from __future__ import annotations

from enum import Enum

__all__ = ["StrEnum"]


class StrEnum(str, Enum):
    """Python 3.10-compatible string enum base."""

    def __str__(self) -> str:
        return str(self.value)
