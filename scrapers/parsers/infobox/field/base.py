from __future__ import annotations

from abc import abstractmethod
from typing import Generic

from scrapers.parsers.infobox.field.protocol import InfoboxFieldParser
from scrapers.parsers.infobox.field.protocol import Input
from scrapers.parsers.infobox.field.protocol import Output


class BaseInfoboxFieldParser(InfoboxFieldParser[Input, Output], Generic[Input, Output]):
    """Common abstract base for infobox field parsers."""

    @abstractmethod
    def parse(self, value: Input) -> Output:
        """Parse raw infobox value into a structured output payload."""


__all__ = ["BaseInfoboxFieldParser", "Input", "Output"]
