from __future__ import annotations

from typing import Any
from typing import Protocol
from typing import runtime_checkable

from bs4 import Tag

from scrapers.parsers.section.extraction_context import SectionExtractionContext
from scrapers.parsers.wiki.element import WikiElementParsers


@runtime_checkable
class StructureParser(Protocol):
    """Kontrakt parsera struktury sekcji/podsekcji/tabel.

    Sekcja jest entrypointem domenowym i dobiera parsery elementarne HTML.
    """

    @property
    def element_parsers(self) -> WikiElementParsers: ...

    def parse_group(
        self,
        elements: list[Tag],
        *,
        context: SectionExtractionContext | None = None,
    ) -> dict[str, Any]: ...


__all__ = ["StructureParser"]
