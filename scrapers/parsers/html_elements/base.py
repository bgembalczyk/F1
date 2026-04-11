from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Generic
from typing import TypeVar

from bs4 import BeautifulSoup
from bs4 import Tag

TOutput = TypeVar("TOutput")


class BaseHtmlElementParser(ABC, Generic[TOutput]):
    """Base contract for single HTML element parsers.

    Single element parsers must accept a bs4.Tag.
    """

    @abstractmethod
    def parse(self, element: Tag) -> TOutput: ...


class BaseHtmlSectionParser(ABC, Generic[TOutput]):
    """Base contract for document/section parsers.

    Document/section parsers are the only parsers that can accept BeautifulSoup.
    """

    @abstractmethod
    def parse(self, soup: BeautifulSoup) -> TOutput: ...
