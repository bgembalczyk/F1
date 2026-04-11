from scrapers.parsers.section.base_nested import BaseNestedSectionParser
from scrapers.parsers.section.wiki.toolbox import SectionParserToolbox
from scrapers.parsers.wiki.sublevels.sub_sub_section import SubSubSectionParser


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
