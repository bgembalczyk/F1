from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any

from bs4 import Tag

from scrapers.parsers.section.extraction_context import SectionExtractionContext
from scrapers.parsers.wiki.element import WikiElementSet


class StructureParser(ABC):
    """Bazowy kontrakt parsera struktury sekcji/podsekcji/tabel."""

    @property
    @abstractmethod
    def element_parsers(self) -> WikiElementSet:
        """Zestaw parserów elementów HTML używany przez parser struktury."""

    @abstractmethod
    def parse(
        self,
        element: Tag,
        *,
        context: SectionExtractionContext | None = None,
    ) -> dict[str, Any]:
        """Publiczny entrypoint parsera struktury."""

    @abstractmethod
    def _parse_group(
        self,
        elements: list[Tag],
        *,
        context: SectionExtractionContext | None = None,
    ) -> dict[str, Any]:
        """Wewnętrzny helper parsujący grupę elementów HTML."""


__all__ = ["StructureParser"]
