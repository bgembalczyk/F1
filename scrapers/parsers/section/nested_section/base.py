from __future__ import annotations

from bs4 import Tag

from scrapers.parsers.nested_child import NestedChildParser
from scrapers.parsers.section.extraction_context import SectionExtractionContext
from scrapers.parsers.section.sub_section.base import SubSectionParser
from scrapers.parsers.section.toolbox import SectionParserToolbox
from scrapers.parsers.section.types import SectionTreePayload
from scrapers.parsers.wiki.recursive import RecursiveSectionParser


class NestedWikiSectionParser(RecursiveSectionParser):
    heading_class = "mw-heading3"
    output_key = "sub_sections"

    def __init__(
        self,
        *,
        child_parser: NestedChildParser | None = None,
        toolbox: SectionParserToolbox | None = None,
    ) -> None:
        super().__init__(
            heading_class=self.heading_class,
            output_key=self.output_key,
            child_parser=child_parser or SubSectionParser(toolbox=toolbox),
            toolbox=toolbox,
        )

    def parse(
        self,
        element: Tag | list[Tag],
        *,
        context: SectionExtractionContext | None = None,
    ) -> SectionTreePayload:
        return super().parse(element, context=context)


__all__ = ["NestedWikiSectionParser"]
