from abc import ABC

from scrapers.parsers.contracts.wiki_elements import WikiSectionElementParserABC


class WikiSectionStructureParserABC(WikiSectionElementParserABC, ABC):
    """Compatibility branch for section structure parsers."""

