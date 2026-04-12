from scrapers.parsers.wiki.sublevels_nested_section.sub_section import SubSectionParser
from scrapers.parsers.wiki.subsubsection.special_cases_router import SpecialCasesSubSubSectionRouter


class SpecialCasesSubSectionParser(SubSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self.child_parser = SpecialCasesSubSubSectionRouter()

