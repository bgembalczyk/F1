from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic
from typing import TypeVar

from bs4 import Tag

from scrapers.parsers.contracts.infobox_fields import InfoboxHtmlFieldParserABC

Output = TypeVar("Output")


@dataclass(frozen=True)
class CallableInfoboxFieldParser(
    InfoboxHtmlFieldParserABC[Output],
    Generic[Output],
):
    _parser: Callable[[Tag], Output]

    def parse(self, value: Tag) -> Output:
        return self._parser(value)
