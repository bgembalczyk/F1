from typing import Any

from bs4 import Tag

from scrapers.parsers.constants import HEADING_CLASS
from scrapers.parsers.section.extraction_context import SectionExtractionContext
from scrapers.parsers.section.nested.wiki import NestedWikiSectionParser
from scrapers.parsers.section.wiki.toolbox import SectionParserToolbox
from scrapers.parsers.section.wiki.toolbox import build_default_section_toolbox
from scrapers.parsers.wiki.base import WikiParser
from scrapers.parsers.wiki.element import build_wikipedia_element_registry
from scrapers.parsers.wiki.element import WikiElementParsers


class ContentTextParser(WikiParser):
    def __init__(
        self,
        *,
        element_parsers: WikiElementParsers | None = None,
        toolbox: SectionParserToolbox | None = None,
    ) -> None:
        self.toolbox = toolbox or build_default_section_toolbox()
        self.section_parser = NestedWikiSectionParser(toolbox=self.toolbox)
        if element_parsers is not None:
            self.toolbox = SectionParserToolbox(
                element_parsers=element_parsers,
                element_registry=build_wikipedia_element_registry(
                    parsers=element_parsers,
                ),
                section_locator=self.toolbox.section_locator,
                section_assembler=self.toolbox.section_assembler,
                domain_mapper=self.toolbox.domain_mapper,
            )
            self.section_parser = NestedWikiSectionParser(toolbox=self.toolbox)

    def parse(
        self,
        element: Tag,
        *,
        page_title: str = "",
        page_url: str = "",
        html_metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        tags = [c for c in element.children if isinstance(c, Tag)]
        parts = self.toolbox.section_locator.locate(tags, heading_class=HEADING_CLASS)
        root_context = SectionExtractionContext(
            page_title=page_title,
            page_url=page_url,
            html_metadata=html_metadata,
        )
        sections: list[dict[str, Any]] = []
        for part in parts:
            section_id = self.toolbox.section_assembler.assemble(
                section_name=part.section_label,
                heading_anchor=part.heading_anchor,
                context=root_context,
                fragment={},
            )["section_id"]
            context = root_context.with_section(
                section_name=part.section_label,
                section_id=section_id,
            )
            fragment = self.section_parser.parse_group(part.elements, context=context)
            sections.append(
                self.toolbox.section_assembler.assemble(
                    section_name=part.section_label,
                    heading_anchor=part.heading_anchor,
                    context=root_context,
                    fragment=fragment,
                ),
            )
        return self.toolbox.domain_mapper.map({"sections": sections})
