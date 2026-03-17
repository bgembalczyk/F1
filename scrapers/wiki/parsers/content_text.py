from typing import Any

from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.constants import HEADING_CLASS
from scrapers.wiki.parsers.section_adapter import SectionExtractionContext
from scrapers.wiki.parsers.section_detection import make_stable_section_id
from scrapers.wiki.parsers.sections.section import SectionParser
from scrapers.wiki.parsers.sections.sub_sub_sub_section import _split_into_parts


class ContentTextParser(WikiParser):
    def __init__(self) -> None:
        self.section_parser = SectionParser()

    def parse(
        self,
        element: Tag,
        *,
        page_title: str = "",
        page_url: str = "",
        html_metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        tags = [c for c in element.children if isinstance(c, Tag)]
        parts = _split_into_parts(tags, HEADING_CLASS)
        root_context = SectionExtractionContext(
            page_title=page_title,
            page_url=page_url,
            html_metadata=html_metadata,
        )
        sections: list[dict[str, Any]] = []
        for name, anchor, group_elements in parts:
            section_id = make_stable_section_id(
                heading_anchor=anchor,
                heading_text=name,
                breadcrumbs=root_context.breadcrumbs,
            )
            context = root_context.with_section(
                section_name=name,
                section_id=section_id,
            )
            sections.append(
                {
                    "section_label": name,
                    "section_id": section_id,
                    **self.section_parser.parse_group(group_elements, context=context),
                },
            )
        return {"sections": sections}
