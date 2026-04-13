from scrapers.parsers.section.sub_sub_section.special_cases_router import (
    SpecialCasesSubSubSectionRouter,
)
from scrapers.parsers.wiki.recursive import RecursiveSectionParser


class SpecialCasesSubSectionParser(RecursiveSectionParser):
    heading_class = "mw-heading4"
    output_key = "sub_sub_sections"

    def __init__(self) -> None:
        super().__init__(child_parser=SpecialCasesSubSubSectionRouter())
