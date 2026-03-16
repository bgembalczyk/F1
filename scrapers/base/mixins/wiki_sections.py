# scrapers/base/wiki_sections.py
from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.helpers.html_utils import find_heading


class WikipediaSectionByIdMixin:
    """Mixin for extracting Wikipedia article sections by anchor/id/text."""

    @staticmethod
    def split_url_fragment(url: str) -> tuple[str, str | None]:
        base_url, fragment = ([*url.split("#", 1), None])[:2]
        if fragment is not None:
            fragment = fragment.lstrip("#").strip() or None
        return base_url, fragment

    def fetch_by_url(self, url: str) -> list[dict[str, Any]]:
        self._original_url = url
        base_url, fragment = self.split_url_fragment(url)
        self.url = base_url
        self._section_fragment = fragment
        return super().fetch()  # type: ignore[misc]

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
                    WikipediaSectionByIdMixin._extract_same_level_header(sib)
                )
                if same_level_header_tag is not None and header_level is not None:
                    sib_level = WikipediaSectionByIdMixin._get_header_level(
                        same_level_header_tag
                    )
                    if sib_level == header_level:
                        break

            collected.append(sib)

        return collected

    @staticmethod
    def extract_section_by_id(
        soup: BeautifulSoup,
        fragment: str,
        *,
        domain: str | None = None,
    ) -> BeautifulSoup | None:
        header = find_heading(soup, fragment, domain=domain)
        if header is None:
            return None

        header_level = WikipediaSectionByIdMixin._get_header_level(header)
        heading_block = WikipediaSectionByIdMixin._get_heading_block(header)
        collected = WikipediaSectionByIdMixin._collect_section_siblings(
            heading_block,
            header_level,
        )

        html = "".join(str(node) for node in collected)
        if not html.strip():
            return None

        return BeautifulSoup(html, "html.parser")
