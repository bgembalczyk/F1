from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Literal

from bs4 import BeautifulSoup
from bs4 import Tag

from models.data.wiki.figure import WikiFigureData
from models.data.wiki.infobox import WikiInfoboxData
from scrapers.parsers.element_parser_abc import HtmlSoupParserABC
from scrapers.parsers.element_parser_abc import HtmlTagParserABC

WikiElementType = Literal[
    "table",
    "list",
    "section",
    "infobox",
    "navbox",
    "references",
    "references_wrap",
    "paragraph",
    "figure",
    "article",
]


class WikiInfoboxElementParserABC(
    HtmlTagParserABC[WikiInfoboxData],
    ABC,
):
    element_type: WikiElementType = "infobox"


class WikiFigureElementParserABC(
    HtmlTagParserABC[WikiFigureData],
    ABC,
):
    element_type: WikiElementType = "figure"


__all__ = [
    "WikiElementType",
    "WikiFigureElementParserABC",
    "WikiInfoboxElementParserABC",
]
