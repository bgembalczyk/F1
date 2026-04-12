from scrapers.parsers.section.toolbox import SectionParserToolbox
from scrapers.parsers.section.sublevels.base_nested_section import BaseNestedSectionParser
from scrapers.parsers.section.sub_sub_section.base import SubSubSectionParser


class SubSectionParser(BaseNestedSectionParser):
    heading_class = "mw-heading4"
    output_key = "sub_sub_sections"

    def __init__(
        self,
        *,
        toolbox: SectionParserToolbox | None = None,
    ) -> None:
        super().__init__(
            child_parser=SubSubSectionParser(toolbox=toolbox),
            toolbox=toolbox,
        )


__all__ = ["SubSectionParser"]
