from bs4 import Tag

from scrapers.parsers.section.extraction_context import SectionExtractionContext
from scrapers.parsers.wiki.base_nested_section.base import BaseNestedSectionParser
from scrapers.parsers.wiki.base_nested_section.sub_section.engine_restrictions import EngineSubSectionParser


class CurrentRulesSectionParser(BaseNestedSectionParser):
    heading_class = "mw-heading3"
    output_key = "sub_sections"

    def __init__(self) -> None:
        self.child_parser = EngineSubSectionParser()
        super().__init__(child_parser=self.child_parser)

    def parse(
        self,
        element: Tag | list[Tag],
        *,
        context: SectionExtractionContext | None = None,
    ) -> dict[str, object]:
        return super().parse(element, context=context)
