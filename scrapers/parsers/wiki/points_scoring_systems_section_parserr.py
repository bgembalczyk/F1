from typing import Any

from scrapers.mixins.apply_for_elements import ApplyForElementsMixin
from scrapers.parsers.table.points_helpers import PointsScoringSystemsHistoryTableMapper
from scrapers.parsers.wiki.nested_wiki import NestedWikiSectionParser
from scrapers.parsers.wiki.shortened_races_sub_sub_section_parser import ShortenedRacesSubSubSectionParser
from scrapers.parsers.wiki.special_cases_sub_section_parser import SpecialCasesSubSectionParser
from scrapers.parsers.wiki.sprint_races_sub_sub_section_parser import SprintRacesSubSubSectionParser


class PointsScoringSystemsSectionParser(ApplyForElementsMixin, NestedWikiSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self.child_parser = SpecialCasesSubSectionParser()
        self._table_parser = PointsScoringSystemsHistoryTableMapper()

    @property
    def sprint_subsection_parser(self) -> SprintRacesSubSubSectionParser:
        router = self.child_parser.child_parser
        return router.sprint_parser

    @property
    def shortened_subsection_parser(self) -> ShortenedRacesSubSubSectionParser:
        router = self.child_parser.child_parser
        return router.shortened_parser

    def collect_rows(self, parsed: dict[str, Any]) -> list[dict[str, Any]]:
        return self._table_parser.collect_rows(parsed)

    def _parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        parsed = super()._parse_group(elements, context=context)
        self.apply_table_mapper(parsed)
        return parsed
