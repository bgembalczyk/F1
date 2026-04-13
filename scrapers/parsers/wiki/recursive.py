from __future__ import annotations

from typing import Any
from typing import TypeAlias

from bs4 import Tag

from scrapers.parsers.mixins.wiki.element import WikiElementParsingMixin
from scrapers.parsers.nested_child import NestedChildParser
from scrapers.parsers.parser_abc import ParserABC
from scrapers.parsers.section.extraction_context import SectionExtractionContext
from scrapers.parsers.section.toolbox import SectionParserToolbox
from scrapers.parsers.section.toolbox import build_default_section_toolbox
from scrapers.parsers.wiki.parser_mixins import NestedSectionHandlingMixin

SectionLevelParseResult: TypeAlias = dict[str, Any]


class RecursiveSectionParser(
    NestedSectionHandlingMixin,
    WikiElementParsingMixin,
    ParserABC,
):
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
    ) -> SectionLevelParseResult:
        elements = list(element.children) if isinstance(element, Tag) else element
        return self._parse_group(elements, context=context)

    def _parse_group(
        self,
        elements: list,
        *,
        context: SectionExtractionContext | None = None,
    ) -> SectionLevelParseResult:
        section_context = context or SectionExtractionContext()
        tags = self.filter_child_tags(elements)
        parts = self.toolbox.section_locator.locate(
            tags,
            heading_class=self.heading_class,
        )
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
            fragment = self._parse_children(part.elements, context=child_context)
            sections.append(
                self.toolbox.section_assembler.assemble(
                    section_name=part.section_label,
                    heading_anchor=part.heading_anchor,
                    context=section_context,
                    fragment=fragment,
                ),
            )

        return {self.output_key: sections}

    def _parse_children(
        self,
        elements: list[Tag],
        *,
        context: SectionExtractionContext,
    ) -> SectionLevelParseResult:
        if self.child_parser is not None:
            return self.child_parser.parse(elements, context=context)
        return {
            "elements": self.parse_elements(
                elements,
                section_context=context,
            ),
        }


__all__ = ["RecursiveSectionParser", "SectionLevelParseResult"]
