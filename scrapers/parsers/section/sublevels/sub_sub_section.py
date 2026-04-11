from scrapers.parsers.section.nested.base import BaseNestedSectionParser
from scrapers.parsers.section.sublevels.sub_sub_sub_section import SubSubSubSectionParser
from scrapers.parsers.wiki.element import WikiElementParsers


class SubSubSectionParser(BaseNestedSectionParser):
    heading_class = "mw-heading5"
    output_key = "sub_sub_sub_sections"

    def __init__(
        self,
        *,
        element_parsers: WikiElementParsers | None = None,
    ) -> None:
        super().__init__(
            child_parser=SubSubSubSectionParser(element_parsers=element_parsers),
        )


__all__ = ["SubSubSectionParser"]
