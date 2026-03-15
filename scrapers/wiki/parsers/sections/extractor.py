from __future__ import annotations

from dataclasses import dataclass

from bs4 import BeautifulSoup
from bs4 import Tag


@dataclass(frozen=True)
class WikiSection:
    """Spójna reprezentacja sekcji Wikipedii.

    Ten obiekt jest zwracany niezależnie od tego, czy sekcja została
    zlokalizowana po fragmencie URL, czy po strukturze nagłówków.
    """

    soup: BeautifulSoup
    heading_id: str | None
    heading_text: str
    heading_level: int | None
    matched_by: str


class WikiSectionExtractor:
    """Wyszukuje i wycina sekcje Wikipedii dla różnych layoutów nagłówków."""

    @staticmethod
    def split_url_fragment(url: str) -> tuple[str, str | None]:
        base_url, fragment = ([*url.split("#", 1), None])[:2]
        if fragment is not None:
            fragment = fragment.lstrip("#").strip() or None
        return base_url, fragment

    @staticmethod
    def _find_node_by_id(soup: BeautifulSoup, fragment: str) -> Tag | None:
        candidates = {fragment, fragment.replace(" ", "_"), fragment.replace("_", " ")}
        for cand in candidates:
            node = soup.find(id=cand)
            if node:
                return node
        return None

    @staticmethod
    def _find_header_by_text(soup: BeautifulSoup, fragment: str) -> Tag | None:
        target_text = fragment.replace("_", " ").strip().lower()
        for h in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
            if (h.get_text(strip=True) or "").lower() == target_text:
                return h
            span = h.find("span", class_="mw-headline")
            if span and (span.get_text(strip=True) or "").lower() == target_text:
                return h
        return None

    @staticmethod
    def _extract_header_from_node(node: Tag) -> Tag | None:
        if node.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            return node
        return node.find_parent(["h1", "h2", "h3", "h4", "h5", "h6"])

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
            if "mw-heading" in classes and parent.find(header.name, recursive=False) is header:
                return parent
        return header

    @staticmethod
    def _extract_same_level_header(sibling: Tag) -> Tag | None:
        if sibling.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            return sibling
        if "mw-heading" in (sibling.get("class") or []):
            return sibling.find(["h1", "h2", "h3", "h4", "h5", "h6"], recursive=False)
        return None

    def _collect_section_nodes(self, heading_block: Tag, header_level: int | None) -> list[object]:
        collected: list[object] = [heading_block]
        for sib in heading_block.next_siblings:
            if isinstance(sib, Tag):
                same_level_header_tag = self._extract_same_level_header(sib)
                if same_level_header_tag is not None and header_level is not None:
                    sib_level = self._get_header_level(same_level_header_tag)
                    if sib_level == header_level:
                        break
            collected.append(sib)
        return collected

    def find_by_fragment(self, soup: BeautifulSoup, fragment: str) -> WikiSection | None:
        node = self._find_node_by_id(soup, fragment)
        header = self._extract_header_from_node(node) if node else None
        matched_by = "id"

        if header is None:
            header = self._find_header_by_text(soup, fragment)
            matched_by = "header_text"
        if header is None:
            return None

        heading_level = self._get_header_level(header)
        heading_block = self._get_heading_block(header)
        nodes = self._collect_section_nodes(heading_block, heading_level)
        html = "".join(str(node_item) for node_item in nodes)
        if not html.strip():
            return None

        return WikiSection(
            soup=BeautifulSoup(html, "html.parser"),
            heading_id=header.get("id"),
            heading_text=header.get_text(" ", strip=True),
            heading_level=heading_level,
            matched_by=matched_by,
        )

