from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Generic
from typing import TypeVar
from typing import Any

from bs4 import Tag

from scrapers.parsers.infobox_parser_abc import InfoboxHtmlFieldParserABC
from scrapers.parsers.infobox_parser_abc import InfoboxRowsParserABC

Output = TypeVar("Output")


class HtmlInfoboxFieldParser(
    InfoboxHtmlFieldParserABC[Output],
    ABC,
    Generic[Output],
):
    """Kontrakt runtime dla parserów pól infoboxu działających na HTML Tag."""

    @abstractmethod
    def parse(self, raw: Tag) -> Output: ...


class InfoboxRowsParser(
    InfoboxRowsParserABC[Output],
    ABC,
    Generic[Output],
):
    """Kontrakt runtime dla parserów pól infoboxu działających na rows."""

    @abstractmethod
    def parse(self, rows: list[dict[str, Any]]) -> Output: ...


__all__ = [
    "HtmlInfoboxFieldParser",
    "InfoboxRowsParser",
    "Output",
]
