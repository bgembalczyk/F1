from scrapers.wiki.parsers.sections.base_nested_section import BaseNestedSectionParser
from scrapers.wiki.parsers.elements.parsers import WikiElementParsers
from scrapers.wiki.parsers.sections.sub_section import SubSectionParser


class SectionParser(BaseNestedSectionParser):
    heading_class = "mw-heading3"
    output_key = "sub_sections"

    def __init__(
        self,
        *,
        element_parsers: WikiElementParsers | None = None,
    ) -> None:
        super().__init__(child_parser=SubSectionParser(element_parsers=element_parsers))
