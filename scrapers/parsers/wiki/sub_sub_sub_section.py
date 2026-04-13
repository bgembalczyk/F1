"""Backward-compatibility shim: SubSubSubSectionParser has been merged into RecursiveSectionParser."""

from __future__ import annotations

from scrapers.parsers.wiki.element import WikiElementSet
from scrapers.parsers.wiki.element import build_wikipedia_element_registry
from scrapers.parsers.mixins.wiki.element import WikiElementParsingMixin
from scrapers.parsers.section.toolbox import SectionParserToolbox
from scrapers.parsers.wiki.recursive import RecursiveSectionParser


class SubSubSubSectionParser(RecursiveSectionParser):
    """Backward-compat alias. Leaf-mode RecursiveSectionParser (heading_class=None)."""

    heading_class = None
    output_key = "elements"

    def __init__(
        self,
        *,
        toolbox: SectionParserToolbox | None = None,
        element_parsers: WikiElementSet | None = None,
    ) -> None:
        super().__init__(toolbox=toolbox)
        if element_parsers is not None:
            WikiElementParsingMixin.__init__(
                self,
                element_parsers=element_parsers,
                element_registry=build_wikipedia_element_registry(
                    parsers=element_parsers,
                ),
            )


__all__ = ["SubSubSubSectionParser"]
