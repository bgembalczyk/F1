from typing import Any

from scrapers.parsers.section.sub_sub_section.shortened_races import ShortenedRacesSubSubSectionParser
from scrapers.parsers.section.sub_sub_section.base import SubSubSectionParser
from scrapers.parsers.section.sub_sub_section.sprint_races import SprintRacesSubSubSectionParser


class SpecialCasesSubSubSectionRouter(SubSubSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self.sprint_parser = SprintRacesSubSubSectionParser()
        self.shortened_parser = ShortenedRacesSubSubSectionParser()

    def _parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        section_id = getattr(context, "section_id", "") or ""
        if "sprint" in section_id.lower():
            return self.sprint_parser.parse(elements, context=context)
        if "shortened" in section_id.lower():
            return self.shortened_parser.parse(elements, context=context)
        parsed = super()._parse_group(elements, context=context)
        self.sprint_parser.apply_table_mapper(parsed)
        self.shortened_parser.apply_table_mapper(parsed)
        return parsed

