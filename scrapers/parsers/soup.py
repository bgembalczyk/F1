from __future__ import annotations

from abc import ABC
from typing import Generic
from typing import TypeVar

from bs4 import BeautifulSoup

from scrapers.parsers.parser_abc import ParserABC

SoupParseResultT_co = TypeVar("SoupParseResultT_co", covariant=True)


class SoupParser(
    ParserABC[BeautifulSoup, SoupParseResultT_co],
    ABC,
    Generic[SoupParseResultT_co],
):
    """Runtime contract for parserów opartych o pełen dokument BeautifulSoup."""


__all__ = ["SoupParser", "SoupParseResultT_co"]
