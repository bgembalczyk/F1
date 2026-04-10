from __future__ import annotations

from typing import Any

from bs4 import Tag

from scrapers.parsers.section.nested.child import NestedChildParser
from scrapers.parsers.section.wiki.detection import make_stable_section_id
from scrapers.parsers.section.wiki.helpers import split_into_parts
from scrapers.parsers.wiki.base import WikiParser


class BaseNestedSectionParser(WikiParser[dict[str, Any]]):
    FAMILY_KIND = "section_parser"

    heading_class: str
    output_key: str

    def __init__(self, *, child_parser: NestedChildParser) -> None:
        self.child_parser = child_parser

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
        parts = split_into_parts(tags, self.heading_class)
        sub_sections: list[dict[str, Any]] = []

        for name, anchor, group_elements in parts:
            section_id = make_stable_section_id(
                heading_anchor=anchor,
                heading_text=name,
                breadcrumbs=section_context.breadcrumbs,
            )
            child_context = section_context.with_section(
                section_name=name,
                section_id=section_id,
            )
            sub_sections.append(
                {
                    "section_label": name,
                    "section_id": section_id,
                    **self.child_parser.parse_group(
                        group_elements,
                        context=child_context,
                    ),
                },
            )

        return {self.output_key: sub_sections}


__all__ = [
    "NestedChildParser",
    "BaseNestedSectionParser",
]
