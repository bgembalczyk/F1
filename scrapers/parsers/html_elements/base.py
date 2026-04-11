from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Generic
from typing import TypeVar

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.parsers.wiki.base import WikiTagParser
from scrapers.domain_roles import Parser

TOutput = TypeVar("TOutput")


class BaseHtmlElementParser(WikiTagParser[TOutput], ABC):
    """Base contract for single HTML element parsers.

    Single element parsers must accept a bs4.Tag.
    """

    @abstractmethod
    def parse(self, raw: Tag) -> TOutput: ...


class BaseHtmlSectionParser(Parser[BeautifulSoup, TOutput], ABC):
    """Base contract for document/section parsers.

    Document/section parsers are the only parsers that can accept BeautifulSoup.
    """

    @abstractmethod
    def parse(self, raw: BeautifulSoup) -> TOutput: ...
