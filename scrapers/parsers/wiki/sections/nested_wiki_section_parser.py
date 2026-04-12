from scrapers.parsers.section.wiki.toolbox import SectionParserToolbox
from scrapers.parsers.wiki.sections.base_nested import BaseNestedSectionParser
from scrapers.parsers.wiki.sections.sublevels.sub_section_parser import SubSectionParser


class NestedWikiSectionParser(BaseNestedSectionParser):
    heading_class = "mw-heading3"
    output_key = "sub_sections"

    def __init__(
        self,
        *,
        toolbox: SectionParserToolbox | None = None,
    ) -> None:
        super().__init__(
            child_parser=SubSectionParser(toolbox=toolbox),
            toolbox=toolbox,
        )


__all__ = ["NestedWikiSectionParser"]
