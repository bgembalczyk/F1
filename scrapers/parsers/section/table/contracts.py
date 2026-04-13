from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any

from bs4 import BeautifulSoup

from scrapers.parsers.element_parser_abc import HtmlSoupParserABC

TablePayload = dict[str, Any]
TableRecord = dict[str, Any]


class SectionTablesHtmlParserABC(HtmlSoupParserABC[list[TablePayload]], ABC):
    """Backward-compat alias. Use HtmlSoupParserABC[list[TablePayload]] directly."""

    @abstractmethod
    def parse(self, raw: BeautifulSoup) -> list[TablePayload]: ...
