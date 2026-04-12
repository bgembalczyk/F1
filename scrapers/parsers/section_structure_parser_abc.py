from abc import ABC

from scrapers.parsers.contracts.section_parser_abc import SectionParserABC


class SectionStructureParserABC(SectionParserABC, ABC):
    """ABC for section parser hierarchy."""

