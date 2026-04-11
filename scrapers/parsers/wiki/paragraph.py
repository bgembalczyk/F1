from models.data.parsed.paragraph import ParagraphParsedData
from scrapers.parsers.html_elements.paragraph import ParagraphElementParser


class ParagraphParser(ParagraphElementParser):
    pass


__all__ = ["ParagraphParser", "ParagraphParsedData"]
