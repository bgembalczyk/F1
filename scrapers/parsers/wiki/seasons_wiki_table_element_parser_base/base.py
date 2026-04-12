from abc import ABC
from abc import abstractmethod
from typing import Any

from bs4 import BeautifulSoup

from scrapers.parsers.wiki.table_element_base import WikiTableElementParserBase


class BaseSeasonParser(WikiTableElementParserBase, ABC):
    """Base contract for season parsers, processing Wikipedia tables."""

    @abstractmethod
    def parse(self, soup: BeautifulSoup, season_year: int | None = None) -> list[dict[str, Any]]: ...

__all__ = ["BaseSeasonParser"]
