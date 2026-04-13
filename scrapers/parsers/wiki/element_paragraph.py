from bs4 import Tag

from models.data.parsed.html_elements import ParagraphElementData
from scrapers.parsers.contracts.wiki_elements import WikiParagraphElementParserABC
from scrapers.parsers.paragraph_element_parser import ParagraphElementParser


class WikiParagraphElementParser(WikiParagraphElementParserABC):
    """Wikipedia HTML element parser for paragraphs."""

    def __init__(self, parser: ParagraphElementParser | None = None) -> None:
        self._parser = parser or ParagraphElementParser()

    def parse(self, raw: Tag) -> ParagraphElementData:
        return self._parser.parse(raw)
