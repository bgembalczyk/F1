from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from models.data.wiki_parser import WikiParserData

if TYPE_CHECKING:
    from collections.abc import Callable

    from bs4 import Tag

    from scrapers.parsers.contracts.html import TagParserABC


@dataclass(frozen=True)
class ParserRule:
    predicate: Callable[[Tag], bool]
    parser: TagParserABC[WikiParserData] | Callable[[Tag], WikiParserData]
    result_type: str
