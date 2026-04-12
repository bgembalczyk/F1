from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Generic
from typing import TypeVar

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.parsers.contracts.base import ParserABC

SoupOut = TypeVar("SoupOut")
TagOut = TypeVar("TagOut")


class SoupParserABC(ParserABC[BeautifulSoup, SoupOut], ABC, Generic[SoupOut]):
    """Canonical parser contract for BeautifulSoup inputs."""

    @abstractmethod
    def parse(self, raw: BeautifulSoup) -> SoupOut: ...


class TagParserABC(ParserABC[Tag, TagOut], ABC, Generic[TagOut]):
    """Canonical parser contract for single bs4.Tag inputs."""

    @abstractmethod
    def parse(self, raw: Tag) -> TagOut: ...


__all__ = ["SoupOut", "TagOut", "SoupParserABC", "TagParserABC"]
