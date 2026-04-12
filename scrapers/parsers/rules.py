from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from models.data.wiki_parser import WikiParserData

if TYPE_CHECKING:
    from collections.abc import Callable

    from bs4 import Tag

    from scrapers.parsers.tag_parser_abc import HtmlTagParserABC


@dataclass(frozen=True)
class ParsingRule:
    predicate: Callable[[Tag], bool]
    parser: HtmlTagParserABC[WikiParserData] | Callable[[Tag], WikiParserData]
    result_type: str


# Backward-compatible alias.
ParserRule = ParsingRule
