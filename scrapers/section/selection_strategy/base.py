from __future__ import annotations

from bs4 import BeautifulSoup


class SectionSelectionStrategy:
    """Strategia obsługi URL artykułu i opcjonalnej selekcji sekcji."""

    def split_url_fragment(self, url: str) -> tuple[str, str | None]:
        return url, None

    def select_article_soup(
        self,
        soup: BeautifulSoup,
        *,
        fragment: str | None,
    ) -> BeautifulSoup:
        _ = fragment
        return soup

    def extract_section_by_id(
        self,
        soup: BeautifulSoup,
        fragment: str,
        *,
        domain: str | None = None,
    ) -> BeautifulSoup | None:
        _ = soup, fragment, domain
        return None


__all__ = ["SectionSelectionStrategy"]
