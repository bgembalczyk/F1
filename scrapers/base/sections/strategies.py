from __future__ import annotations

from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.helpers.html_utils import find_heading


class UrlFragmentStrategy:
    """Obsługa URL z fragmentem sekcji (np. ``#History``)."""

    @staticmethod
    def split_url_fragment(url: str) -> tuple[str, str | None]:
        base_url, fragment = ([*url.split("#", 1), None])[:2]
        if fragment is not None:
            fragment = fragment.lstrip("#").strip() or None
        return base_url, fragment

    def apply(self, scraper: Any, url: str) -> None:
        base_url, fragment = self.split_url_fragment(url)
        scraper._original_url = url
        scraper.url = base_url
        scraper._section_fragment = fragment


class SectionSelectionStrategy:
    """Selekcja i ekstrakcja sekcji artykułu Wikipedii."""

    @staticmethod
    def _get_header_level(header: Tag) -> int | None:
        try:
            return int(header.name[1])
        except (TypeError, ValueError, IndexError):
            return None

    @staticmethod
    def _get_heading_block(header: Tag) -> Tag:
        parent = header.parent
        if isinstance(parent, Tag):
            classes = parent.get("class") or []
            if (
                "mw-heading" in classes
                and parent.find(header.name, recursive=False) is header
            ):
                return parent
        return header

    @staticmethod
    def _extract_same_level_header(sibling: Tag) -> Tag | None:
        if sibling.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            return sibling
        if "mw-heading" in (sibling.get("class") or []):
            return sibling.find(["h1", "h2", "h3", "h4", "h5", "h6"], recursive=False)
        return None

    @classmethod
    def _collect_section_siblings(
        cls,
        heading_block: Tag,
        header_level: int | None,
    ) -> list[Any]:
        collected: list[Any] = [heading_block]

        for sib in heading_block.next_siblings:
            if isinstance(sib, Tag):
                same_level_header_tag = cls._extract_same_level_header(sib)
                if same_level_header_tag is not None and header_level is not None:
                    sib_level = cls._get_header_level(same_level_header_tag)
                    if sib_level == header_level:
                        break

            collected.append(sib)

        return collected

    @classmethod
    def extract_section_by_id(
        cls,
        soup: BeautifulSoup,
        fragment: str,
        *,
        domain: str | None = None,
    ) -> BeautifulSoup | None:
        header = find_heading(soup, fragment, domain=domain)
        if header is None:
            return None
        return cls.extract_section_by_heading(header)

    @classmethod
    def extract_section_by_heading(cls, header: Tag) -> BeautifulSoup | None:
        header_level = cls._get_header_level(header)
        heading_block = cls._get_heading_block(header)
        collected = cls._collect_section_siblings(heading_block, header_level)

        html = "".join(str(node) for node in collected)
        if not html.strip():
            return None

        return BeautifulSoup(html, "html.parser")

    def select(
        self,
        soup: BeautifulSoup,
        *,
        fragment: str | None,
        domain: str | None = None,
    ) -> BeautifulSoup:
        if not fragment:
            return soup
        return self.extract_section_by_id(soup, fragment, domain=domain) or soup

