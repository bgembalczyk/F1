from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any

from bs4 import Tag

from scrapers.parsers.section.extraction_context import SectionExtractionContext


class NestedChildParser(ABC):
    """Kontrakt parsera obsługującego zagnieżdżoną grupę elementów sekcji."""

    @abstractmethod
    def parse(
        self,
        elements: list[Tag],
        *,
        context: SectionExtractionContext | None = None,
    ) -> dict[str, Any]:
        """Publiczny entrypoint parsera dzieci sekcji."""


__all__ = ["NestedChildParser"]
