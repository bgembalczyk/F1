from bs4 import Tag

from models.data.parsed.paragraph import ParagraphParsedData
from scrapers.parsers.paragraph_element_parser import ParagraphElementParser


class WikiParagraphParser(ParagraphElementParser):
    def parse(self, raw: Tag) -> ParagraphParsedData:
        return super().parse(raw)


# ``ParagraphParser`` is the canonical public name for this parser.
ParagraphParser = WikiParagraphParser


__all__ = ["ParagraphParser", "WikiParagraphParser", "ParagraphParsedData"]
