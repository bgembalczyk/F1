from __future__ import annotations

from typing import Any
from typing import Protocol
from typing import runtime_checkable


@runtime_checkable
class TableParserProtocol(Protocol):
    def parse(self, fragment: dict[str, Any]) -> dict[str, Any] | None: ...


__all__ = ["TableParserProtocol"]
