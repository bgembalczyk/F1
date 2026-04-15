from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import TypeVar

from bs4 import Tag

from scrapers.parsers.parser_abc import ParserABC

Output = TypeVar("Output")


class InfoboxFieldParserABC(ABC, Generic[Output]):
    """Merged base class for all infobox field parsers (HTML Tag or normalized rows)."""


class InfoboxHtmlFieldParserABC(InfoboxFieldParserABC[Output], ParserABC[Tag, Output], ABC, Generic[Output]):
    """Parser contract for a single infobox field parsed directly from HTML Tag."""

    @abstractmethod
    def parse(self, raw: Tag) -> Output: ...


class InfoboxRowsParserABC(
    InfoboxFieldParserABC[Output],
    ParserABC[list[dict[str, Any]], Output],
    ABC,
    Generic[Output],
):
    """Parser contract for infobox field data already normalized into rows."""

    @abstractmethod
    def parse(self, rows: list[dict[str, Any]]) -> Output: ...


__all__ = [
    "InfoboxFieldParserABC",
    "InfoboxHtmlFieldParserABC",
    "InfoboxRowsParserABC",
]
