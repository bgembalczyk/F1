from bs4 import Tag

from scrapers.parsers.section.extraction_context import SectionExtractionContext
from scrapers.parsers.wiki.base_nested_section.sub_section.base import SubSectionParser
from scrapers.parsers.wiki.base_nested_section.sub_sub_section.special_cases_router import SpecialCasesSubSubSectionRouter


class SpecialCasesSubSectionParser(SubSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self.child_parser = SpecialCasesSubSubSectionRouter()

    def parse(
        self,
        element: Tag | list[Tag],
        *,
        context: SectionExtractionContext | None = None,
    ) -> dict[str, object]:
        return super().parse(element, context=context)
