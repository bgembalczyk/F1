from dataclasses import replace
from typing import Any

from bs4 import Tag

from scrapers.parsers.constants import HEADING_CLASS
from scrapers.parsers.parser_abc import ParserABC
from scrapers.parsers.section.extraction_context import SectionExtractionContext
from scrapers.parsers.section.nested_section.base import NestedWikiSectionParser
from scrapers.parsers.section.toolbox import SectionParserToolbox
from scrapers.parsers.section.toolbox import build_default_section_toolbox
from scrapers.parsers.wiki.element import WikiElementSet
from scrapers.parsers.wiki.element import build_wikipedia_element_registry


class ContentTextParser(ParserABC):
    def __init__(
        self,
        *,
        element_parsers: WikiElementSet | None = None,
        toolbox: SectionParserToolbox | None = None,
    ) -> None:
        self.toolbox = toolbox or build_default_section_toolbox()
        self.section_parser = NestedWikiSectionParser(toolbox=self.toolbox)
        if element_parsers is not None:
            section_first_parsers = replace(
                element_parsers,
                section_parser=self.section_parser.parse,
            )
            self.toolbox = SectionParserToolbox(
                element_parsers=section_first_parsers,
                element_registry=build_wikipedia_element_registry(
                    parsers=section_first_parsers,
                ),
                section_locator=self.toolbox.section_locator,
                section_assembler=self.toolbox.section_assembler,
                mapper_registry=self.toolbox.mapper_registry,
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

        # pipeline: extract section -> parse elements -> map domain
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
            fragment = self.section_parser.parse(part.elements, context=context)
            sections.append(
                self.toolbox.section_assembler.assemble(
                    section_name=part.section_label,
                    heading_anchor=part.heading_anchor,
                    context=root_context,
                    fragment=fragment,
                ),
            )
        return self.toolbox.mapper_registry.domain_mapper.map({"sections": sections})
