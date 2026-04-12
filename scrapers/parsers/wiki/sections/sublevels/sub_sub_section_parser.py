from scrapers.parsers.wiki.sections.base_nested import BaseNestedSectionParser
from scrapers.parsers.wiki.sections.sublevels.sub_sub_sub_section_parser import SubSubSubSectionParser
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
