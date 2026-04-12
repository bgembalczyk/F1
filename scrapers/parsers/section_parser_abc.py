"""Compatibility layer for legacy section parser ABC imports.

Canonical runtime bases live in:
- ``scrapers.parsers.wiki.section.base.BaseSectionParser`` for domain section parsers,
- ``scrapers.parsers.nested_child.NestedChildParser`` for nested section parsers.
"""

from scrapers.parsers.nested_child import NestedChildParser
from scrapers.parsers.wiki.section.base import BaseSectionParser

SectionParserABC = BaseSectionParser
NestedSectionParserABC = NestedChildParser
SubSectionParserABC = NestedChildParser
SubSubSectionParserABC = NestedChildParser

__all__ = [
    "SectionParserABC",
    "NestedSectionParserABC",
    "SubSectionParserABC",
    "SubSubSectionParserABC",
]
