from scrapers.parsers.section.nested_section.base import NestedWikiSectionParser
from scrapers.parsers.section.sub_section.engine_regulation import (
    EngineRegulationSubSectionParser,
)


class HistorySectionParser(NestedWikiSectionParser):
    def __init__(self) -> None:
        super().__init__(child_parser=EngineRegulationSubSectionParser())
