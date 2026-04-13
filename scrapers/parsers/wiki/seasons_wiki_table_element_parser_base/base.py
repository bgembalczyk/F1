from abc import ABC
from abc import abstractmethod
from typing import Any

from bs4 import BeautifulSoup

from scrapers.parsers.element_parser_abc import HtmlSoupParserABC
from scrapers.parsers.wiki.base import WikiRecords


class BaseSeasonParser(HtmlSoupParserABC[WikiRecords], ABC):
    """Base contract for season parsers, processing Wikipedia tables."""

    @abstractmethod
    def parse(self, soup: BeautifulSoup, season_year: int | None = None) -> list[dict[str, Any]]: ...

__all__ = ["BaseSeasonParser"]
