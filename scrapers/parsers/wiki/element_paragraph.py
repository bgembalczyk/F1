from bs4 import Tag

from models.data.parsed.html_elements import ParagraphElementData
from scrapers.parsers.html_elements.paragraph_element_parser import ParagraphElementParser


class WikiParagraphElementParser(ParagraphElementParser):
    """Wikipedia HTML element parser for paragraphs."""

    def parse(self, raw: Tag) -> ParagraphElementData:
        return super().parse(raw)
