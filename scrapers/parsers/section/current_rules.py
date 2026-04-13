from scrapers.parsers.section.sub_section.engine_restrictions import (
    EngineSubSectionParser,
)
from scrapers.parsers.wiki.recursive import RecursiveSectionParser


class CurrentRulesSectionParser(RecursiveSectionParser):
    heading_class = "mw-heading3"
    output_key = "sub_sections"

    def __init__(self) -> None:
        super().__init__(child_parser=EngineSubSectionParser())
