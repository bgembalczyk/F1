from __future__ import annotations

from abc import abstractmethod
from typing import Generic

from bs4 import Tag

from scrapers.parsers.infobox.field.protocol import InfoboxFieldParser
from scrapers.parsers.infobox.field.protocol import Output


class BaseInfoboxFieldParser(InfoboxFieldParser[Output], Generic[Output]):
    """Common abstract base for infobox field parsers."""

    @abstractmethod
    def parse(self, value: Tag) -> Output:
        """Parse raw infobox value into a structured output payload."""


__all__ = ["BaseInfoboxFieldParser", "Output"]
