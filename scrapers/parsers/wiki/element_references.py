from bs4 import Tag

from models.data.parsed.references_wrap import ReferencesWrapParsedData
from scrapers.parsers.wiki.references_wrap import ReferencesWrapParser


class WikiReferencesElementParser(ReferencesWrapParser):
    """Wikipedia HTML element parser for references wrappers."""

    def parse(self, element: Tag) -> ReferencesWrapParsedData:
        return super().parse(element)
