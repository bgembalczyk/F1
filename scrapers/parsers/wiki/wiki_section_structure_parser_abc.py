from abc import ABC

from scrapers.parsers.contracts.wiki_elements import WikiSectionParserABC


class WikiSectionStructureParserABC(WikiSectionParserABC, ABC):
    """Compatibility branch for section structure parsers."""

