from scrapers.parsers.section.nested.base import BaseNestedSectionParser
from scrapers.parsers.section.sub.base import SubSectionParser
from scrapers.parsers.wiki.elements.parsers import WikiElementParsers


class NestedWikiSectionParser(BaseNestedSectionParser):
    heading_class = "mw-heading3"
    output_key = "sub_sections"

    def __init__(
        self,
        *,
        element_parsers: WikiElementParsers | None = None,
    ) -> None:
        super().__init__(child_parser=SubSectionParser(element_parsers=element_parsers))


__all__ = ["NestedWikiSectionParser"]
