from abc import ABC

from scrapers.parsers.wiki.wiki_section_parser_abc import WikiSectionParserABC


class WikiSectionStructureParserABC(WikiSectionParserABC, ABC):
    """Compatibility branch for section structure parsers."""

