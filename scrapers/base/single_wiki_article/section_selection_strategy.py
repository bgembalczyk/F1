from __future__ import annotations

from abc import ABC
from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.helpers.html_utils import find_heading


class SectionSelectionStrategy(ABC):
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


class WikipediaSectionByIdSelectionStrategy(SectionSelectionStrategy):
    """Strategia oparta o wyszukiwanie sekcji Wikipedii po identyfikatorze."""

    def __init__(
        self,
        *,
        domain: str | None = None,
        fallback_to_article: bool = True,
    ) -> None:
        self.domain = domain
        self.fallback_to_article = fallback_to_article

    def split_url_fragment(self, url: str) -> tuple[str, str | None]:
        base_url, fragment = ([*url.split("#", 1), None])[:2]
        if fragment is not None:
            fragment = fragment.lstrip("#").strip() or None
        return base_url, fragment

    def select_article_soup(
        self,
        soup: BeautifulSoup,
        *,
        fragment: str | None,
    ) -> BeautifulSoup:
        if not fragment:
            return soup
        section = self.extract_section_by_id(soup, fragment, domain=self.domain)
        if section is None and self.fallback_to_article:
            return soup
        return section or soup

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

    @staticmethod
    def _collect_section_siblings(
        heading_block: Tag,
        header_level: int | None,
    ) -> list[Any]:
        collected: list[Any] = [heading_block]

        for sib in heading_block.next_siblings:
            if isinstance(sib, Tag):
                same_level_header_tag = (
                    WikipediaSectionByIdSelectionStrategy._extract_same_level_header(
                        sib,
                    )
                )
                if same_level_header_tag is not None and header_level is not None:
                    sib_level = WikipediaSectionByIdSelectionStrategy._get_header_level(
                        same_level_header_tag,
                    )
                    if sib_level == header_level:
                        break

            collected.append(sib)

        return collected

    def extract_section_by_id(
        self,
        soup: BeautifulSoup,
        fragment: str,
        *,
        domain: str | None = None,
    ) -> BeautifulSoup | None:
        effective_domain = domain or self.domain
        header = find_heading(soup, fragment, domain=effective_domain)
        if header is None:
            return None
        return self.extract_section_by_heading(header)

    @staticmethod
    def extract_section_by_heading(header: Tag) -> BeautifulSoup | None:
        header_level = WikipediaSectionByIdSelectionStrategy._get_header_level(header)
        heading_block = WikipediaSectionByIdSelectionStrategy._get_heading_block(header)
        collected = WikipediaSectionByIdSelectionStrategy._collect_section_siblings(
            heading_block,
            header_level,
        )

        html = "".join(str(node) for node in collected)
        if not html.strip():
            return None

        return BeautifulSoup(html, "html.parser")
