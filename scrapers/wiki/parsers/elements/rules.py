from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from bs4 import Tag

    from scrapers.wiki.parsers.types import WikiParserData


@dataclass(frozen=True)
class ParserRule:
    predicate: Callable[[Tag], bool]
    parser: Callable[[Tag], WikiParserData]
    result_type: str
