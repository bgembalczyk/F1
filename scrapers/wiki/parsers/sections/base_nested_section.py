from __future__ import annotations

from typing import Any
from typing import Protocol

from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.sections.data_classes import SectionExtractionContext
from scrapers.wiki.parsers.sections.detection import make_stable_section_id
from scrapers.wiki.parsers.sections.helpers import _split_into_parts


class NestedChildParser(Protocol):
    def parse_group(
        self,
        elements: list,
        *,
        context: SectionExtractionContext | None = None,
    ) -> dict[str, Any]: ...


class BaseNestedSectionParser(WikiParser):
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
        parts = _split_into_parts(tags, self.heading_class)
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
