from typing import Any

from bs4 import BeautifulSoup

from scrapers.wiki.parsers.sections.extractor import WikiSectionExtractor


class WikipediaSectionByIdMixin:
    """Backward-compatible mixin delegating section extraction to wiki parsers."""

    @staticmethod
    def split_url_fragment(url: str) -> tuple[str, str | None]:
        return WikiSectionExtractor.split_url_fragment(url)

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
    ) -> BeautifulSoup | None:
        section = WikiSectionExtractor().find_by_fragment(soup, fragment)
        return section.soup if section is not None else None
