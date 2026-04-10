from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.section.selection_strategy.base import SectionSelectionStrategy


class SingleArticleSectionAwareMixin:
    """Mixin realizujący strategię fragmentów/sekcji artykułu."""

    section_selection_strategy: SectionSelectionStrategy | None
    _section_fragment: str | None

    def __init__(
        self,
        *,
        section_selection_strategy: SectionSelectionStrategy | None = None,
        **kwargs: Any,
    ) -> None:
        self.section_selection_strategy = section_selection_strategy
        self._section_fragment: str | None = None
        super().__init__(**kwargs)

    def extract_by_url(self, url: str) -> list[dict[str, Any]]:
        self._original_url = url
        if self.section_selection_strategy is None:
            self.url = url
            self._section_fragment = None
            return super().fetch()

        base_url, fragment = self.section_selection_strategy.split_url_fragment(url)
        self.url = base_url
        self._section_fragment = fragment
        return super().fetch()

    def _prepare_article_soup(self, soup: BeautifulSoup) -> BeautifulSoup:
        if self.section_selection_strategy is None:
            return soup
        return self.section_selection_strategy.select_article_soup(
            soup,
            fragment=self._section_fragment,
        )

    def extract_section_by_id(
        self,
        soup: BeautifulSoup,
        section_id: str,
        *,
        domain: str | None = None,
    ) -> BeautifulSoup | None:
        if self.section_selection_strategy is None:
            return None
        return self.section_selection_strategy.extract_section_by_id(
            soup,
            section_id,
            domain=domain,
        )


__all__ = ["SingleArticleSectionAwareMixin"]
