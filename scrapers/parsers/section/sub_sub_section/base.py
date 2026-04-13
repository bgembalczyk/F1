"""Backward-compatibility shim: SubSubSectionParser has been merged into RecursiveSectionParser."""

from scrapers.parsers.wiki.recursive import RecursiveSectionParser


class SubSubSectionParser(RecursiveSectionParser):
    """Backward-compat alias. Inherit RecursiveSectionParser directly with heading_class='mw-heading5'."""

    heading_class = "mw-heading5"
    output_key = "sub_sub_sub_sections"


__all__ = ["SubSubSectionParser"]
