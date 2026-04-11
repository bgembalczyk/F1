from scrapers.parsers.section.nested.base import BaseNestedSectionParser
from scrapers.parsers.section.sublevels.sub_section import SubSectionParser
from scrapers.parsers.section.wiki.toolbox import SectionParserToolbox


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
