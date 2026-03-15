from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import Protocol

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser

ArticleParseResult = dict[str, Any] | list[Any] | None


class ArticleParser(Protocol):
    """Protokół parsera działającego na całym artykule (BeautifulSoup)."""

    def parse_article(self, soup: BeautifulSoup) -> ArticleParseResult:
        """Parsuje cały artykuł i zwraca dane domenowe."""


@dataclass(slots=True)
class CallableArticleParserAdapter:
    """Cienki adapter funkcji `BeautifulSoup -> wynik` do ArticleParser."""

    parser_fn: Any

    def parse_article(self, soup: BeautifulSoup) -> ArticleParseResult:
        return self.parser_fn(soup)


@dataclass(slots=True)
class WikiParserArticleAdapter:
    """Adapter z kontraktu `WikiParser.parse(Tag)` do `ArticleParser`."""

    parser: WikiParser
    locator: Any

    def parse_article(self, soup: BeautifulSoup) -> ArticleParseResult:
        element = self.locator(soup)
        if element is None or not isinstance(element, Tag):
            return None
        return self.parser.parse(element)

