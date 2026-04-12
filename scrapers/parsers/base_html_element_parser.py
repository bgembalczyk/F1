from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TypeVar

from bs4 import Tag

from scrapers.parsers.element_parser_abc import ElementParserABC

TOutput = TypeVar("TOutput")


class BaseHtmlElementParser(ElementParserABC[TOutput], ABC):
    """Base contract for single HTML element parsers.

    Single element parsers must accept a bs4.Tag.
    """

    @abstractmethod
    def parse(self, raw: Tag) -> TOutput: ...

