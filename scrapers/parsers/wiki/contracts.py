from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any

from bs4 import Tag

from scrapers.parsers.roles import HtmlTagParserABC


class AbstractWikiElementParser(ABC, HtmlTagParserABC[dict[str, Any]]):
    """Bazowy kontrakt runtime parsera pojedynczego elementu HTML Wikipedii."""

    @abstractmethod
    def parse(self, element: Tag, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Parsuje pojedynczy element HTML Wikipedii do słownika danych."""


WikiElementParserABC = AbstractWikiElementParser


__all__ = [
    "AbstractWikiElementParser",
    "WikiElementParserABC",
]
