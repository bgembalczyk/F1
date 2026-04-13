from scrapers.parsers.section.sub_section.engine_regulation import (
    EngineRegulationSubSectionParser,
)
from scrapers.parsers.wiki.recursive import RecursiveSectionParser


class HistorySectionParser(RecursiveSectionParser):
    heading_class = "mw-heading3"
    output_key = "sub_sections"

    def __init__(self) -> None:
        super().__init__(child_parser=EngineRegulationSubSectionParser())
