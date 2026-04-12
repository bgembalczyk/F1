from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from models.data.parsed.figure import FigureParsedData
from models.data.parsed.infobox import InfoboxParsedData
from models.data.parsed.nav_box import NavBoxParsedData
from scrapers.parsers.roles import HtmlTagParserABC
from scrapers.parsers.roles import ListHtmlParserABC
from scrapers.parsers.roles import MapperABC
from scrapers.parsers.roles import TableHtmlParserABC
from scrapers.parsers.roles import TableMapperABC

WikiTableParsedData = dict[str, Any]
WikiListParsedData = dict[str, Any]
WikiSectionParsedData = dict[str, Any]


class WikiTableParserABC(TableHtmlParserABC, ABC):
    pass


class WikiListParserABC(ListHtmlParserABC, ABC):
    pass


class WikiSectionStructureParserABC(MapperABC[BeautifulSoup | Tag, WikiSectionParsedData], ABC):
    pass


class WikiInfoboxParserABC(HtmlTagParserABC[InfoboxParsedData], ABC):
    pass


class WikiNavboxHtmlParserABC(HtmlTagParserABC[NavBoxParsedData], ABC):
    pass


class WikiFigureHtmlParserABC(HtmlTagParserABC[FigureParsedData], ABC):
    pass


@dataclass(frozen=True)
class WikiTableMapperSet:
    """Registry mapperów tabel (etap translacji parse -> domain)."""

    table_mapper: TableMapperABC | None = None


__all__ = [
    "WikiFigureHtmlParserABC",
    "WikiInfoboxParserABC",
    "WikiListParsedData",
    "WikiListParserABC",
    "WikiNavboxHtmlParserABC",
    "WikiSectionParsedData",
    "WikiSectionStructureParserABC",
    "WikiTableMapperSet",
    "WikiTableParsedData",
    "WikiTableParserABC",
]
