from scrapers.wiki.parsers.sections.base_nested_section import BaseNestedSectionParser
from scrapers.wiki.parsers.sections.sub_section import SubSectionParser


class SectionParser(BaseNestedSectionParser):
    heading_class = "mw-heading3"
    output_key = "sub_sections"

    def __init__(self) -> None:
        super().__init__(child_parser=SubSectionParser())
