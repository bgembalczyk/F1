"""Backward compatible wrappers for legacy imports.

Prefer ``WikipediaSectionByIdSelectionStrategy`` from
``scrapers.base.single_wiki_article.section_selection_strategy``.
"""

from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.single_wiki_article.section_selection_strategy import (
    WikipediaSectionByIdSelectionStrategy,
)


class WikipediaSectionByIdMixin:
    """Legacy mixin delegujący do implementacji strategii sekcji."""

    _strategy = WikipediaSectionByIdSelectionStrategy()

    @staticmethod
    def split_url_fragment(url: str) -> tuple[str, str | None]:
        return WikipediaSectionByIdSelectionStrategy().split_url_fragment(url)

    def fetch_by_url(self, url: str) -> list[dict[str, Any]]:
        self._original_url = url
        base_url, fragment = self.split_url_fragment(url)
        self.url = base_url
        self._section_fragment = fragment
        return super().fetch()  # type: ignore[misc]

    @staticmethod
    def extract_section_by_id(
        soup: BeautifulSoup,
        fragment: str,
        *,
        domain: str | None = None,
    ) -> BeautifulSoup | None:
        return WikipediaSectionByIdSelectionStrategy(
            domain=domain,
        ).extract_section_by_id(
            soup,
            fragment,
            domain=domain,
        )

    @staticmethod
    def extract_section_by_heading(header: Tag) -> BeautifulSoup | None:
        return WikipediaSectionByIdSelectionStrategy.extract_section_by_heading(header)
