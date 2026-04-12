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

TIn = TypeVar("TIn")
TOut = TypeVar("TOut")
TElementOut = TypeVar("TElementOut")


class BaseWikiParser(Parser[TIn, TOut], ABC, Generic[TIn, TOut]):
    """Canonical parser contract: parse(input) -> output."""

    @abstractmethod
    def parse(self, raw: TIn) -> TOut: ...


class ElementParser(BaseWikiParser[Tag, TElementOut], ABC, Generic[TElementOut]):
    """Parser pojedynczego elementu HTML (bs4.Tag)."""


class SectionParser(BaseWikiParser[BeautifulSoup, SectionParseResult], ABC):
    """Parser sekcji HTML (BeautifulSoup -> SectionParseResult)."""


class TableParser(BaseWikiParser[BeautifulSoup, Any], ABC):
    """Parser tabel HTML oparty o dokument/fragment soup."""


class ListParser(ElementParser[dict[str, Any]], ABC):
    """Parser list HTML (<ul>/<ol>)."""


class InfoboxParser(ElementParser[dict[str, Any]], ABC):
    """Parser infoboxów HTML."""


__all__ = [
    "BaseWikiParser",
    "ElementParser",
    "InfoboxParser",
    "ListParser",
    "SectionParser",
    "TableParser",
]
