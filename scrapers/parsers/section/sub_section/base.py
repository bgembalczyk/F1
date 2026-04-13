"""Backward-compatibility shim: SubSectionParser has been merged into RecursiveSectionParser."""

from scrapers.parsers.wiki.recursive import RecursiveSectionParser


class SubSectionParser(RecursiveSectionParser):
    """Backward-compat alias. Inherit RecursiveSectionParser directly with heading_class='mw-heading4'."""

    heading_class = "mw-heading4"
    output_key = "sub_sub_sections"


__all__ = ["SubSectionParser"]
