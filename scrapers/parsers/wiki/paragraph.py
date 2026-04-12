from models.data.parsed.paragraph import ParagraphParsedData
from scrapers.parsers.html_elements.paragraph_element_parser import ParagraphElementParser


class WikiParagraphParser(ParagraphElementParser):
    pass


__all__ = ["WikiParagraphParser", "ParagraphParsedData"]
