from bs4 import Tag

from models.data.parsed.references_wrap import ReferencesWrapParsedData
from scrapers.parsers.element_parser_abc import HtmlTagParserABC
from scrapers.parsers.wiki.references_wrap import ReferencesWrapParser
from scrapers.parsers.wiki.wiki_element_parser_abc import WikiElementType


class WikiReferencesElementParser(ReferencesWrapParser, HtmlTagParserABC[ReferencesWrapParsedData]):
    """Wikipedia HTML element parser for references wrappers."""

    element_type: WikiElementType = "references"

    def parse(self, raw: Tag) -> ReferencesWrapParsedData:
        return super().parse(raw)
