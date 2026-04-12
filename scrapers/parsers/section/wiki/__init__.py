"""scrapers.parsers.section.wiki — canonical section parsing facade.

Provides ``SectionParser`` (the top-level section tree parser) and re-exports
the public wiki-section parsing API so that callers can use the stable path
``scrapers.parsers.section.wiki`` instead of the internal implementation paths.
"""

from scrapers.parsers.section.nested_section.base import NestedWikiSectionParser as SectionParser

__all__ = ["SectionParser"]
