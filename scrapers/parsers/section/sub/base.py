from scrapers.parsers.section.nested.base import BaseNestedSectionParser
from scrapers.parsers.section.sub.sub.base import SubSubSectionParser
from scrapers.parsers.wiki.elements.parsers import WikiElementParsers


class SubSectionParser(BaseNestedSectionParser):
    heading_class = "mw-heading4"
    output_key = "sub_sub_sections"

    def __init__(
        self,
        *,
        element_parsers: WikiElementParsers | None = None,
    ) -> None:
        super().__init__(
            child_parser=SubSubSectionParser(element_parsers=element_parsers),
        )


__all__ = ["SubSectionParser"]
