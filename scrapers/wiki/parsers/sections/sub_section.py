from scrapers.wiki.parsers.sections.base_nested_section import BaseNestedSectionParser
from scrapers.wiki.parsers.sections.sub_sub_section import SubSubSectionParser


class SubSectionParser(BaseNestedSectionParser):
    heading_class = "mw-heading4"
    output_key = "sub_sub_sections"

    def __init__(self) -> None:
        super().__init__(child_parser=SubSubSectionParser())
