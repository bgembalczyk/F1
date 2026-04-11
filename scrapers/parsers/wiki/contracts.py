from __future__ import annotations

from typing import Any
from typing import Protocol
from typing import runtime_checkable

from bs4 import Tag

from scrapers.parsers.roles import HtmlElementParser


@runtime_checkable
class WikiElementParser(HtmlElementParser[dict[str, Any]], Protocol):
    """Kontrakt parsera pojedynczego elementu HTML Wikipedii."""

    def parse(self, element: Tag, *args: Any, **kwargs: Any) -> dict[str, Any]: ...


__all__ = ["WikiElementParser"]
