from collections.abc import Callable
from dataclasses import dataclass

from bs4 import Tag

from models.data.wiki_parser import WikiParserData
from scrapers.parsers.parser_abc import ParserABC


@dataclass(frozen=True)
class WikiElementSet:
    infobox_parser: ParserABC[Tag, WikiParserData]
    paragraph_parser: ParserABC[Tag, WikiParserData]
    figure_parser: ParserABC[Tag, WikiParserData]
    list_parser: ParserABC[Tag, WikiParserData]
    table_html_parser: ParserABC[Tag, WikiParserData]
    navbox_parser: ParserABC[Tag, WikiParserData]
    references_wrap_parser: ParserABC[Tag, WikiParserData]
    references_parser: ParserABC[Tag, WikiParserData]
    section_parser: Callable[[Tag], WikiParserData] | None = None
