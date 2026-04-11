from __future__ import annotations

from typing import Any
from typing import Protocol
from typing import runtime_checkable

from bs4 import Tag

from scrapers.parsers.section.extraction_context import SectionExtractionContext


@runtime_checkable
class StructureParser(Protocol):
    """Kontrakt parsera struktury sekcji/podsekcji/tabel."""

    def parse_group(
        self,
        elements: list[Tag],
        *,
        context: SectionExtractionContext | None = None,
    ) -> dict[str, Any]: ...


__all__ = ["StructureParser"]
