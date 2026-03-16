from typing import Any

from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.section_adapter import SectionExtractionContext
from scrapers.wiki.parsers.section_detection import make_stable_section_id
from scrapers.wiki.parsers.sections.sub_sub_section import SubSubSectionParser
from scrapers.wiki.parsers.sections.sub_sub_sub_section import _split_into_parts

_HEADING_CLASS = "mw-heading4"


class SubSectionParser(WikiParser):
    def __init__(self) -> None:
        self.sub_sub_section_parser = SubSubSectionParser()

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
        parts = _split_into_parts(tags, _HEADING_CLASS)
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
                    **self.sub_sub_section_parser.parse_group(
                        group_elements,
                        context=child_context,
                    ),
                },
            )
        return {"sub_sub_sections": sub_sections}
