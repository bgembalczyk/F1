from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import TypeVar

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.domain_roles import Parser
from scrapers.section.parse_results import SectionParseResult

OutputT = TypeVar("OutputT")


class SoupParserABC(Parser[BeautifulSoup, OutputT], ABC, Generic[OutputT]):
    """Canonical parser contract for BeautifulSoup inputs."""

    @abstractmethod
    def parse(self, raw: BeautifulSoup) -> OutputT: ...


class TagParserABC(Parser[Tag, OutputT], ABC, Generic[OutputT]):
    """Canonical parser contract for single bs4.Tag inputs."""

    @abstractmethod
    def parse(self, raw: Tag) -> OutputT: ...


class SectionParserABC(SoupParserABC[SectionParseResult], ABC):
    """Canonical parser contract for wiki sections."""


class TableParserABC(SoupParserABC[Any], ABC):
    """Canonical parser contract for table-oriented soup parsing."""


class ListParserABC(TagParserABC[dict[str, Any]], ABC):
    """Canonical parser contract for list elements (<ul>/<ol>)."""


class InfoboxParserABC(TagParserABC[dict[str, Any]], ABC):
    """Canonical parser contract for infobox elements."""


__all__ = [
    "InfoboxParserABC",
    "ListParserABC",
    "SectionParserABC",
    "SoupParserABC",
    "TableParserABC",
    "TagParserABC",
]
