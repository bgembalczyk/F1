from __future__ import annotations

from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from models.data.parsed.html_elements import SectionElementData
from scrapers.parsers.contracts.wiki_elements import WikiSectionElementParserABC
from scrapers.parsers.wiki.content_text import ContentTextParser


class SectionElementParser(WikiSectionElementParserABC):
    """Document parser for article sections (BeautifulSoup input only)."""

    def __init__(self, content_text_parser: ContentTextParser | None = None) -> None:
        self._content_text_parser = content_text_parser or ContentTextParser()

    def parse(self, raw: BeautifulSoup) -> SectionElementData:
        soup = raw
        content = self._find_content_text(soup)
        if content is None:
            return {"sections": []}
        parsed: dict[str, Any] = self._content_text_parser.parse(content)
        sections = parsed.get("sections")
        return {"sections": sections if isinstance(sections, list) else []}

    @staticmethod
    def _find_content_text(soup: BeautifulSoup) -> Tag | None:
        content = soup.find(
            "div",
            id=lambda x: isinstance(x, str) and "content-text" in x,
        )
        return content if isinstance(content, Tag) else None
