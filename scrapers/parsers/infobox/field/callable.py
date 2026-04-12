from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
from typing import Generic

from bs4 import Tag

from scrapers.parsers.infobox.field.protocol import HtmlInfoboxFieldParser
from scrapers.parsers.infobox.field.protocol import Output


@dataclass(frozen=True)
class CallableInfoboxFieldParser(
    HtmlInfoboxFieldParser[Output],
    Generic[Output],
):
    _parser: Callable[[Tag], Output]

    def parse(self, value: Tag) -> Output:
        return self._parser(value)
