from __future__ import annotations

from abc import ABC
from typing import TypeVar

from scrapers.parsers.roles import HtmlElementParserABC

TOutput = TypeVar("TOutput")


class BaseHtmlElementParser(HtmlElementParserABC[TOutput], ABC):
    """Base contract for single HTML element parsers."""
