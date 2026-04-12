from scrapers.parsers.section.toolbox import SectionParserToolbox
from scrapers.parsers.wiki.base_nested import BaseNestedSectionParser
from scrapers.parsers.wiki.sublevels.sub_sub_sub_section import SubSubSubSectionParser


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
