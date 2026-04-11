from __future__ import annotations

from typing import Any

from bs4 import Tag

from scrapers.parsers.section.extraction_context import SectionExtractionContext
from scrapers.parsers.section.nested.child import NestedChildParser
from scrapers.parsers.section.wiki.toolbox import SectionParserToolbox
from scrapers.parsers.section.wiki.toolbox import build_default_section_toolbox
from scrapers.parsers.wiki.base import WikiParser


class BaseNestedSectionParser(WikiParser[Tag, dict[str, Any]]):
    heading_class: str
    output_key: str

    def __init__(
        self,
        *,
        child_parser: NestedChildParser,
        toolbox: SectionParserToolbox | None = None,
    ) -> None:
        self.child_parser = child_parser
        self.toolbox = toolbox or build_default_section_toolbox()

    @property
    def element_parsers(self):
        return self.toolbox.element_parsers

    def parse(
        self,
        element: Tag,
        *,
        context: SectionExtractionContext | None = None,
    ) -> dict[str, Any]:
        return self.parse_group(list(element.children), context=context)

    def parse_group(
        self,
        elements: list,
        *,
        context: SectionExtractionContext | None = None,
    ) -> dict[str, Any]:
        section_context = context or SectionExtractionContext()
        tags = [c for c in elements if isinstance(c, Tag)]
        parts = self.toolbox.section_locator.locate(
            tags, heading_class=self.heading_class
        )
        sub_sections: list[dict[str, Any]] = []

        for part in parts:
            section_id = self.toolbox.section_assembler.assemble(
                section_name=part.section_label,
                heading_anchor=part.heading_anchor,
                context=section_context,
                fragment={},
            )["section_id"]
            child_context = section_context.with_section(
                section_name=part.section_label,
                section_id=section_id,
            )
            fragment = self.child_parser.parse_group(
                part.elements,
                context=child_context,
            )
            sub_sections.append(
                self.toolbox.section_assembler.assemble(
                    section_name=part.section_label,
                    heading_anchor=part.heading_anchor,
                    context=section_context,
                    fragment=fragment,
                ),
            )

        return {self.output_key: sub_sections}


__all__ = [
    "NestedChildParser",
    "BaseNestedSectionParser",
]
