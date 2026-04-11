from scrapers.parsers.section.nested.base import BaseNestedSectionParser
from scrapers.parsers.section.sublevels.sub_sub_sub_section import SubSubSubSectionParser
from scrapers.parsers.section.wiki.toolbox import SectionParserToolbox


class SubSubSectionParser(BaseNestedSectionParser):
    heading_class = "mw-heading5"
    output_key = "sub_sub_sub_sections"

    def __init__(
        self,
        *,
        toolbox: SectionParserToolbox | None = None,
    ) -> None:
        super().__init__(
            child_parser=SubSubSubSectionParser(toolbox=toolbox),
            toolbox=toolbox,
        )


__all__ = ["SubSubSectionParser"]
