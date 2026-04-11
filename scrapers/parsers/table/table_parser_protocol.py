from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import Protocol
from typing import runtime_checkable

if TYPE_CHECKING:
    from scrapers.parsers.input_types import WikiDictFragmentInput


@runtime_checkable
class TableParserProtocol(Protocol):
    def parse(self, fragment: WikiDictFragmentInput) -> dict[str, Any] | None: ...


__all__ = ["TableParserProtocol"]
