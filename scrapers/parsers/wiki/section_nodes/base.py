from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any

from bs4 import Tag

from scrapers.parsers.section.extraction_context import SectionExtractionContext


class WikiSectionNodeParserABC(ABC):
    """Single base contract for section-node parsers."""

    @abstractmethod
    def parse(
        self,
        elements: list[Tag],
        *,
        context: SectionExtractionContext | None = None,
    ) -> dict[str, Any]: ...


__all__ = ["WikiSectionNodeParserABC"]
