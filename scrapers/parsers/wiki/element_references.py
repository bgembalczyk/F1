from bs4 import Tag

from models.data.parsed.references_wrap import ReferencesWrapParsedData
from scrapers.parsers.wiki.references_wrap import ReferencesWrapParser


from scrapers.parsers.wiki.element_bases import WikiReferencesParserBase


class WikiReferencesElementParser(ReferencesWrapParser, WikiReferencesParserBase):
    """Wikipedia HTML element parser for references wrappers."""

    def parse(self, raw: Tag) -> ReferencesWrapParsedData:
        return super().parse(raw)
