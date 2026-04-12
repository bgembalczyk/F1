from bs4 import Tag

from scrapers.parsers.section.extraction_context import SectionExtractionContext
from scrapers.parsers.section.toolbox import SectionParserToolbox
from scrapers.parsers.wiki.base_nested_section.base import BaseNestedSectionParser
from scrapers.parsers.wiki.base_nested_section.sub_section.base import SubSectionParser


class NestedWikiSectionParser(BaseNestedSectionParser):
    heading_class = "mw-heading3"
    output_key = "sub_sections"

    def __init__(
        self,
        *,
        toolbox: SectionParserToolbox | None = None,
    ) -> None:
        super().__init__(
            child_parser=SubSectionParser(toolbox=toolbox),
            toolbox=toolbox,
        )

    def parse(
        self,
        element: Tag | list[Tag],
        *,
        context: SectionExtractionContext | None = None,
    ) -> dict[str, object]:
        return super().parse(element, context=context)


__all__ = ["NestedWikiSectionParser"]
