from bs4 import Tag

from models.data.parsed.references_wrap import ReferencesWrapParsedData
from scrapers.parsers.contracts.wiki_elements import WikiReferencesElementParserABC
from scrapers.parsers.wiki.references_wrap import ReferencesWrapParser


class WikiReferencesElementParser(ReferencesWrapParser, WikiReferencesElementParserABC):
    """Wikipedia HTML element parser for references wrappers."""

    def parse(self, raw: Tag) -> ReferencesWrapParsedData:
        return super().parse(raw)
