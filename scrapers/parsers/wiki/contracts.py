from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Protocol
from typing import runtime_checkable

from bs4 import Tag

from scrapers.parsers.roles import HtmlElementParser


class AbstractWikiElementParser(ABC, HtmlElementParser[dict[str, Any]]):
    """Bazowy kontrakt runtime parsera pojedynczego elementu HTML Wikipedii."""

    @abstractmethod
    def parse(self, element: Tag, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Parsuje pojedynczy element HTML Wikipedii do słownika danych."""


@runtime_checkable
class WikiElementParserProtocol(Protocol):
    """Typing-only kontrakt parsera pojedynczego elementu HTML Wikipedii."""

    def parse(self, element: Tag, *args: Any, **kwargs: Any) -> dict[str, Any]: ...


__all__ = [
    "AbstractWikiElementParser",
    "WikiElementParserProtocol",
]
