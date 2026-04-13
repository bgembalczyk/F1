from scrapers.parsers.section.sub_section.base import SubSectionParser
from scrapers.parsers.section.sub_sub_section.special_cases_router import (
    SpecialCasesSubSubSectionRouter,
)


class SpecialCasesSubSectionParser(SubSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self.child_parser = SpecialCasesSubSubSectionRouter()
