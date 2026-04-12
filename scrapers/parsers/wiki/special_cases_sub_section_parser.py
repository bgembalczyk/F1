from scrapers.parsers.wiki.special_cases_sub_sub_section_router import SpecialCasesSubSubSectionRouter
from scrapers.parsers.wiki.sublevels.sub_section import SubSectionParser


class SpecialCasesSubSectionParser(SubSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self.child_parser = SpecialCasesSubSubSectionRouter()

