from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import TypeVar

from bs4 import Tag

from scrapers.parsers.element_parser_abc import HtmlTagParserABC
from scrapers.parsers.parser_abc import ParserABC

Output = TypeVar("Output")


class InfoboxParserABC(HtmlTagParserABC[dict[str, Any]], ABC):
    """Coordinator parser contract for the whole infobox."""

    @abstractmethod
    def parse(self, raw: Tag) -> dict[str, Any]: ...


class InfoboxHtmlFieldParserABC(HtmlTagParserABC[Output], ABC, Generic[Output]):
    """Parser contract for a single infobox field parsed directly from HTML Tag."""

    @abstractmethod
    def parse(self, raw: Tag) -> Output: ...


class InfoboxRowsParserABC(
    ParserABC[list[dict[str, Any]], Output],
    ABC,
    Generic[Output],
):
    """Parser contract for infobox field data already normalized into rows."""

    @abstractmethod
    def parse(self, rows: list[dict[str, Any]]) -> Output: ...


class InfoboxCellParserABC(HtmlTagParserABC[dict[str, Any]], ABC):
    """Parser contract for a single infobox table cell."""

    @abstractmethod
    def parse(self, raw: Tag) -> dict[str, Any]: ...


class InfoboxNestedTableParserABC(ParserABC[Tag, dict[str, Any]], ABC):
    """Parser contract for nested tables embedded in infobox cells."""

    @abstractmethod
    def parse(self, raw: Tag) -> dict[str, Any]: ...


class InfoboxCollapsibleTableParserABC(ParserABC[Tag, dict[str, Any] | None], ABC):
    """Parser contract for collapsible infobox tables."""

    @abstractmethod
    def parse(self, raw: Tag) -> dict[str, Any] | None: ...


__all__ = [
    "InfoboxCellParserABC",
    "InfoboxCollapsibleTableParserABC",
    "InfoboxHtmlFieldParserABC",
    "InfoboxNestedTableParserABC",
    "InfoboxParserABC",
    "InfoboxRowsParserABC",
]
