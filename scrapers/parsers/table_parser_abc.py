from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any

from bs4 import Tag

from scrapers.parsers.element_parser_abc import HtmlTagParserABC


class TableParserABC(HtmlTagParserABC[dict[str, Any]], ABC):
    """Parser contract for full table payload extraction."""

    @abstractmethod
    def parse(self, raw: Tag) -> dict[str, Any]: ...


class TableRowParserABC(HtmlTagParserABC[dict[str, Any]], ABC):
    """Parser contract for a single table row."""

    @abstractmethod
    def parse(self, raw: Tag) -> dict[str, Any]: ...


class TableCellParserABC(HtmlTagParserABC[dict[str, Any]], ABC):
    """Parser contract for a single table cell."""

    @abstractmethod
    def parse(self, raw: Tag) -> dict[str, Any]: ...
