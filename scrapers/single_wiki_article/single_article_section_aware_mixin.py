from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.section.selection_strategy.base import SectionSelectionStrategy


class SectionAwareMixin:
    """Mixin exposing section-selection helpers for article scrapers."""

    section_selection_strategy: SectionSelectionStrategy | None

    def __init__(
        self,
        *,
        section_selection_strategy: SectionSelectionStrategy | None = None,
        **kwargs: Any,
    ) -> None:
        if section_selection_strategy is not None:
            self.section_selection_strategy = section_selection_strategy
        super().__init__(**kwargs)

    def extract_section_by_id(
        self,
        soup: BeautifulSoup,
        section_id: str,
        *,
        domain: str | None = None,
    ) -> BeautifulSoup | None:
        strategy = getattr(self, "section_selection_strategy", None)
        if strategy is None:
            return None
        return strategy.extract_section_by_id(
            soup,
            section_id,
            domain=domain,
        )




__all__ = ["SectionAwareMixin"]
