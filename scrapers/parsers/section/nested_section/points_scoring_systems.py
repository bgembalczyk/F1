from typing import Any

from scrapers.mixins.apply_for_elements import ApplyForElementsMixin
from scrapers.parsers.table.points_helpers import PointsScoringSystemsHistoryTableMapper
from scrapers.parsers.section.nested_section.base import NestedWikiSectionParser
from scrapers.parsers.section.sub_section.special_cases import SpecialCasesSubSectionParser
from scrapers.parsers.section.sub_sub_section.shortened_races import ShortenedRacesSubSubSectionParser
from scrapers.parsers.section.sub_sub_section.sprint_races import SprintRacesSubSubSectionParser


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
