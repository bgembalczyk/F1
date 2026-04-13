"""Backward-compatibility shim: NestedWikiSectionParser has been merged into RecursiveSectionParser."""

from scrapers.parsers.wiki.recursive import RecursiveSectionParser


class NestedWikiSectionParser(RecursiveSectionParser):
    """Backward-compat alias. Inherit RecursiveSectionParser directly."""

    heading_class = "mw-heading3"
    output_key = "sub_sections"


__all__ = ["NestedWikiSectionParser"]
