from models.data.parsed.paragraph import ParagraphParsedData
from scrapers.parsers.html_elements.paragraph import ParagraphElementParser


class WikiParagraphParser(ParagraphElementParser):
    pass


# Backward-compatible alias.
ParagraphParser = WikiParagraphParser

__all__ = ["WikiParagraphParser", "ParagraphParser", "ParagraphParsedData"]
