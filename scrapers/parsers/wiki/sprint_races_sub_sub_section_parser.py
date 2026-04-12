from typing import Any

from scrapers.mixins.apply_for_elements import ApplyForElementsMixin
from scrapers.parsers.table.points_helpers import SprintPointsTableMapper
from scrapers.parsers.wiki.sublevels.sub_sub_section import SubSubSectionParser


class SprintRacesSubSubSectionParser(ApplyForElementsMixin, SubSubSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self._table_parser = SprintPointsTableMapper()

    def collect_rows(self, parsed: dict[str, Any]) -> list[dict[str, Any]]:
        return self._table_parser.collect_rows(parsed)

    def _parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        parsed = super()._parse_group(elements, context=context)
        if not parsed.get("sub_sub_sub_sections"):
            parsed = self.child_parser.parse(elements, context=context)
        self.apply_table_mapper(parsed)
        return parsed

