from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any

from bs4 import Tag

from scrapers.parsers.section.extraction_context import SectionExtractionContext


class NestedChildParser(ABC):
    """Kontrakt parsera obsługującego zagnieżdżoną grupę elementów sekcji."""

    @abstractmethod
    def parse_group(
        self,
        elements: list[Tag],
        *,
        context: SectionExtractionContext | None = None,
    ) -> dict[str, Any]:
        """Parsuje dzieci sekcji do mapy danych."""


__all__ = ["NestedChildParser"]
