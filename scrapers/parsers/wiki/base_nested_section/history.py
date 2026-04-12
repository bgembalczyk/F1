from scrapers.parsers.wiki.base_nested import BaseNestedSectionParser
from scrapers.parsers.wiki.engine_regulation_sub_section_parser import EngineRegulationSubSectionParser


class HistorySectionParser(BaseNestedSectionParser):
    heading_class = "mw-heading3"
    output_key = "sub_sections"

    def __init__(self) -> None:
        self.child_parser = EngineRegulationSubSectionParser()
        super().__init__(child_parser=self.child_parser)
