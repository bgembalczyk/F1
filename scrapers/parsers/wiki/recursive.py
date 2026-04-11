from __future__ import annotations

from typing import Any

from bs4 import Tag

from scrapers.parsers.mixins.wiki.element import WikiElementParsingMixin
from scrapers.parsers.nested_child import NestedChildParser
from scrapers.parsers.section.extraction_context import SectionExtractionContext
from scrapers.parsers.section.wiki.toolbox import SectionParserToolbox
from scrapers.parsers.section.wiki.toolbox import build_default_section_toolbox
from scrapers.parsers.wiki.base import WikiParser


class RecursiveSectionParser(WikiElementParsingMixin, WikiParser):
    """Generic recursive parser for heading levels h2-h6."""

    def __init__(
        self,
        *,
        heading_class: str,
        output_key: str,
        child_parser: NestedChildParser | None = None,
        toolbox: SectionParserToolbox | None = None,
    ) -> None:
        self.heading_class = heading_class
        self.output_key = output_key
        self.child_parser = child_parser
        self.toolbox = toolbox or build_default_section_toolbox()
        WikiElementParsingMixin.__init__(
            self,
            element_parsers=self.toolbox.element_parsers,
            element_registry=self.toolbox.element_registry,
        )

    @property
    def element_parsers(self):
        return self.toolbox.element_parsers

    def parse(
        self,
        element: Tag | list[Tag],
        *,
        context: SectionExtractionContext | None = None,
    ) -> dict[str, Any]:
        if isinstance(element, Tag):
            return self._parse_group(list(element.children), context=context)
        return self._parse_group(element, context=context)

    def _parse_group(
        self,
        elements: list,
        *,
        context: SectionExtractionContext | None = None,
    ) -> dict[str, Any]:
        section_context = context or SectionExtractionContext()
        tags = [c for c in elements if isinstance(c, Tag)]
        parts = self.toolbox.section_locator.locate(tags, heading_class=self.heading_class)
        sections: list[dict[str, Any]] = []

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
            fragment = (
                self.child_parser.parse(part.elements, context=child_context)
                if self.child_parser is not None
                else {
                    "elements": self.parse_elements(
                        part.elements,
                        section_context=child_context,
                    )
                }
            )
            sections.append(
                self.toolbox.section_assembler.assemble(
                    section_name=part.section_label,
                    heading_anchor=part.heading_anchor,
                    context=section_context,
                    fragment=fragment,
                ),
            )

        return {self.output_key: sections}


__all__ = ["RecursiveSectionParser"]
