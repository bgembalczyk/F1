from typing import Any

from bs4 import Tag

from scrapers.parsers.constants import HEADING_CLASS
from scrapers.parsers.section.extraction_context import SectionExtractionContext
from scrapers.parsers.section.nested.wiki import NestedWikiSectionParser
from scrapers.parsers.section.wiki.detection import make_stable_section_id
from scrapers.parsers.section.wiki.helpers import split_into_parts
from scrapers.parsers.wiki.base import WikiParser
from scrapers.parsers.element import WikiElementParsers


class ContentTextParser(WikiParser):
    def __init__(
        self,
        *,
        element_parsers: WikiElementParsers | None = None,
    ) -> None:
        self.section_parser = NestedWikiSectionParser(element_parsers=element_parsers)

    def parse(
        self,
        element: Tag,
        *,
        page_title: str = "",
        page_url: str = "",
        html_metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        tags = [c for c in element.children if isinstance(c, Tag)]
        parts = split_into_parts(tags, HEADING_CLASS)
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
