from __future__ import annotations

from typing import Any
from typing import Protocol


class RecordSplitStrategy(Protocol):
    def apply(self, record: dict[str, Any]) -> list[dict[str, Any]]:
        """Split a record into zero, one, or many records."""


class SplitRule(Protocol):
    def should_apply(self, record: dict[str, Any]) -> bool:
        """Return True when a strategy branch should run for this record."""
