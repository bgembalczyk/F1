from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Generic

from bs4 import Tag

from scrapers.parsers.constants_contracts import TagOut
from scrapers.parsers.tag_parser_abc import HtmlTagParserABC


class ElementParserABC(HtmlTagParserABC[TagOut], ABC, Generic[TagOut]):
    """Canonical contract for HTML element parsers (list/table/infobox/navbox/references)."""

    @abstractmethod
    def parse(self, raw: Tag) -> TagOut: ...

