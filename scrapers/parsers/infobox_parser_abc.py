from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any

from bs4 import Tag

from scrapers.parsers.tag_parser_abc import HtmlTagParserABC


class InfoboxParserABC(HtmlTagParserABC[dict[str, Any]], ABC):
    """Coordinator parser contract for the whole infobox."""

    @abstractmethod
    def parse(self, raw: Tag) -> dict[str, Any]: ...


class InfoboxFieldParserABC(HtmlTagParserABC[Any], ABC):
    """Parser contract for a single infobox field."""

    @abstractmethod
    def parse(self, raw: Tag) -> Any: ...


class InfoboxCellParserABC(HtmlTagParserABC[dict[str, Any]], ABC):
    """Parser contract for a single infobox table cell."""

    @abstractmethod
    def parse(self, raw: Tag) -> dict[str, Any]: ...

