from scrapers.parsers.section.sublevels.base_nested_section import BaseNestedSectionParser
from scrapers.parsers.section.sub_section.engine_regulation import EngineRegulationSubSectionParser


class HistorySectionParser(BaseNestedSectionParser):
    heading_class = "mw-heading3"
    output_key = "sub_sections"

    def __init__(self) -> None:
        self.child_parser = EngineRegulationSubSectionParser()
        super().__init__(child_parser=self.child_parser)
