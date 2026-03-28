# scrapers/base/wiki_sections.py
from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.sections.strategies import SectionSelectionStrategy
from scrapers.base.sections.strategies import UrlFragmentStrategy


class WikipediaSectionByIdMixin:
    """Mixin for extracting Wikipedia article sections by anchor/id/text."""

    @staticmethod
    def split_url_fragment(url: str) -> tuple[str, str | None]:
        return UrlFragmentStrategy.split_url_fragment(url)

    def fetch_by_url(self, url: str) -> list[dict[str, Any]]:
        UrlFragmentStrategy().apply(self, url)
        return super().fetch()  # type: ignore[misc]

    @staticmethod
    def _get_header_level(header: Tag) -> int | None:
        return SectionSelectionStrategy._get_header_level(header)

    @staticmethod
    def _get_heading_block(header: Tag) -> Tag:
        return SectionSelectionStrategy._get_heading_block(header)

    @staticmethod
    def _extract_same_level_header(sibling: Tag) -> Tag | None:
        return SectionSelectionStrategy._extract_same_level_header(sibling)

    @staticmethod
    def _collect_section_siblings(
        heading_block: Tag,
        header_level: int | None,
    ) -> list[Any]:
        return SectionSelectionStrategy._collect_section_siblings(
            heading_block,
            header_level,
        )

    @staticmethod
    def extract_section_by_id(
        soup: BeautifulSoup,
        fragment: str,
        *,
        domain: str | None = None,
    ) -> BeautifulSoup | None:
        return SectionSelectionStrategy.extract_section_by_id(
            soup,
            fragment,
            domain=domain,
        )

    @staticmethod
    def extract_section_by_heading(header: Tag) -> BeautifulSoup | None:
        return SectionSelectionStrategy.extract_section_by_heading(header)
