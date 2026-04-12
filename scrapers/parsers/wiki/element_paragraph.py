from bs4 import Tag

from models.data.parsed.html_elements import ParagraphElementData
from scrapers.parsers.paragraph_element_parser import ParagraphElementParser
from scrapers.parsers.wiki.wiki_element_parser_abc import WikiParagraphElementParserABC


class WikiParagraphElementParser(WikiParagraphElementParserABC):
    """Wikipedia HTML element parser for paragraphs."""

    def __init__(self, parser: ParagraphElementParser | None = None) -> None:
        self._parser = parser or ParagraphElementParser()

    def parse(self, raw: Tag) -> ParagraphElementData:
        return self._parser.parse(raw)
