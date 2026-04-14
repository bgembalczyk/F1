from bs4 import Tag

from models.data.parsed.html_elements import ParagraphElementData
from scrapers.parsers.element_parser_abc import HtmlTagParserABC
from scrapers.parsers.paragraph_element_parser import ParagraphElementParser
from scrapers.parsers.wiki.wiki_element_parser_abc import WikiElementType


class WikiParagraphElementParser(HtmlTagParserABC[ParagraphElementData]):
    """Wikipedia HTML element parser for paragraphs."""

    element_type: WikiElementType = "paragraph"

    def __init__(self, parser: ParagraphElementParser | None = None) -> None:
        self._parser = parser or ParagraphElementParser()

    def parse(self, raw: Tag) -> ParagraphElementData:
        return self._parser.parse(raw)
