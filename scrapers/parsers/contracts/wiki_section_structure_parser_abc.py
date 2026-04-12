from abc import ABC

from scrapers.parsers.contracts.wiki_section_parser_abc import WikiSectionParserABC


class WikiSectionStructureParserABC(WikiSectionParserABC, ABC):
    """Compatibility branch for section structure parsers."""

