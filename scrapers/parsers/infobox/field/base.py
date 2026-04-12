from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import TypeVar

from bs4 import Tag

from scrapers.parsers.contracts.infobox_fields import InfoboxHtmlFieldParserABC
from scrapers.parsers.contracts.infobox_fields import InfoboxRowsParserABC

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
