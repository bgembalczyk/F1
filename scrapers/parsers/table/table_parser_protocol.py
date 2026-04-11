from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import Protocol
from typing import runtime_checkable

if TYPE_CHECKING:
    from scrapers.parsers.input_types import WikiDictFragmentInput


@runtime_checkable
class TableFragmentParserProtocol(Protocol):
    """Typing-only kontrakt parsera fragmentu tabeli."""

    def parse(self, fragment: WikiDictFragmentInput) -> dict[str, Any] | None: ...


# Backward-compatible alias
TableParserProtocol = TableFragmentParserProtocol


__all__ = ["TableFragmentParserProtocol", "TableParserProtocol"]
