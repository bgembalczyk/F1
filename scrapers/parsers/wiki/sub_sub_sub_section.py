from __future__ import annotations

from bs4 import Tag

from models.payload import WikiParsedPayload
from scrapers.parsers.mixins.wiki.element import WikiElementParsingMixin
from scrapers.parsers.section.extraction_context import SectionExtractionContext
from scrapers.parsers.section.toolbox import SectionParserToolbox
from scrapers.parsers.section.toolbox import build_default_section_toolbox
from scrapers.parsers.wiki.element import WikiElementSet
from scrapers.parsers.wiki.element import build_wikipedia_element_registry
from scrapers.parsers.wiki.recursive import RecursiveSectionParser


class SubSubSubSectionParser(RecursiveSectionParser):
    output_key = "elements"

    def __init__(
        self,
        *,
        toolbox: SectionParserToolbox | None = None,
        element_parsers: WikiElementSet | None = None,
    ) -> None:
        effective_toolbox = toolbox or build_default_section_toolbox()
        super().__init__(
            heading_class="mw-heading6",
            output_key=self.output_key,
            child_parser=None,
            toolbox=effective_toolbox,
        )
        if element_parsers is not None:
            WikiElementParsingMixin.__init__(
                self,
                element_parsers=element_parsers,
                element_registry=build_wikipedia_element_registry(
                    parsers=element_parsers,
                ),
            )

    def _parse_group(
        self,
        elements: list,
        *,
        context: SectionExtractionContext | None = None,
    ) -> dict[str, object]:
        section_context = context or SectionExtractionContext()
        tags = [c for c in elements if isinstance(c, Tag)]
        return {"elements": self.parse_elements(tags, section_context=section_context)}

    def parse_group(
        self,
        elements: list,
        *,
        context: SectionExtractionContext | None = None,
    ) -> dict[str, list[WikiParsedPayload]]:
        return self._parse_group(elements, context=context)


__all__ = ["SubSubSubSectionParser"]
