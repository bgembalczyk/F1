from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from models.data.wiki_parser import WikiParserData

if TYPE_CHECKING:
    from collections.abc import Callable

    from bs4 import Tag

    from scrapers.parsers.parser_abc import ParserABC


@dataclass(frozen=True)
class ParsingRule:
    predicate: Callable[[Tag], bool]
    parser: ParserABC[Tag, WikiParserData] | Callable[[Tag], WikiParserData]
    result_type: str


ParserRule = ParsingRule
