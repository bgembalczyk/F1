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


__all__ = [
    "InfoboxHtmlFieldParserABC",
    "InfoboxParserABC",
    "InfoboxRowsParserABC",
]
