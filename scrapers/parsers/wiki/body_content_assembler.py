from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.parsers.body_content_adapter import BodyContentAdapter
from scrapers.parsers.parser_abc import ParserABC
from scrapers.parsers.wiki.category_links import CategoryLinksParser
from scrapers.parsers.wiki.content_text import ContentTextParser
from scrapers.parsers.wiki.element import WikiElementSet


class BodyContentAssembler(ParserABC[Tag, dict[str, Any]]):
    """Składa wynik głównej treści strony Wikipedii z dedykowanych parserów."""

    def __init__(
        self,
        *,
        element_parsers: WikiElementSet | None = None,
        body_content_adapter: BodyContentAdapter | None = None,
    ) -> None:
        self.body_content_adapter = body_content_adapter or BodyContentAdapter()
        self.category_links_parser = CategoryLinksParser()
        self.content_text_parser = ContentTextParser(element_parsers=element_parsers)

    def parse(self, element: Tag) -> dict[str, Any]:
        parts = self.body_content_adapter.adapt(element)
        return {
            "category_links": (
                self.category_links_parser.parse(parts.catlinks)
                if isinstance(parts.catlinks, Tag)
                else None
            ),
            "content_text": (
                self.content_text_parser.parse(parts.content_text)
                if isinstance(parts.content_text, Tag)
                else None
            ),
        }

    @staticmethod
    def find_body_content(soup: BeautifulSoup) -> Tag | None:
        return BodyContentAdapter.find_body_content(soup)


BodyContentParser = BodyContentAssembler

__all__ = ["BodyContentAssembler", "BodyContentParser"]
