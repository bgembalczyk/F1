from models.data.parsed.paragraph import ParagraphParsedData
from scrapers.parsers.paragraph_element_parser import ParagraphElementParser


class WikiParagraphParser(ParagraphElementParser):
    pass


# ``ParagraphParser`` is the canonical public name for this parser.
ParagraphParser = WikiParagraphParser


__all__ = ["ParagraphParser", "WikiParagraphParser", "ParagraphParsedData"]
