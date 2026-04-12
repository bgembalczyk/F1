from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import TypeVar

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.domain_roles import Parser

InT = TypeVar("InT")
OutT = TypeVar("OutT")


class WikiParserABC(Parser[InT, OutT], ABC, Generic[InT, OutT]):
    """Oficjalny kontrakt parsera wiki (input -> output)."""

    @abstractmethod
    def parse(self, raw: InT) -> OutT: ...


class ElementParserABC(WikiParserABC[InT, OutT], ABC, Generic[InT, OutT]):
    """Wspólny kontrakt parserów elementów artykułu wiki."""


class TableElementParserABC(ElementParserABC[Tag, dict[str, Any]], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> dict[str, Any]: ...


class ListElementParserABC(ElementParserABC[Tag, dict[str, Any]], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> dict[str, Any]: ...


class SectionElementParserABC(
    ElementParserABC[BeautifulSoup | Tag, dict[str, Any]],
    ABC,
):
    @abstractmethod
    def parse(self, raw: BeautifulSoup | Tag) -> dict[str, Any]: ...


class InfoboxElementParserABC(ElementParserABC[Tag, dict[str, Any]], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> dict[str, Any]: ...


__all__ = [
    "ElementParserABC",
    "InfoboxElementParserABC",
    "ListElementParserABC",
    "SectionElementParserABC",
    "TableElementParserABC",
    "WikiParserABC",
]
