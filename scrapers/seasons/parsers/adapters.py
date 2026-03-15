from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from bs4 import BeautifulSoup

from scrapers.wiki.parsers.article import ArticleParseResult
from scrapers.wiki.parsers.article import ArticleParser


@dataclass(slots=True)
class SeasonParserAdapter:
    """Cienki adapter parsera domenowego sezonu do wspólnego kontraktu."""

    key: str
    parser_fn: Any

    def parse_article(self, soup: BeautifulSoup) -> ArticleParseResult:
        return self.parser_fn(soup)


@dataclass(slots=True)
class SeasonParsersPipeline(ArticleParser):
    """Łączy wiele parserów domenowych sezonu w jeden etap WikiScrapera."""

    parsers: list[SeasonParserAdapter]

    def parse_article(self, soup: BeautifulSoup) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for parser in self.parsers:
            result[parser.key] = parser.parse_article(soup)
        return result

