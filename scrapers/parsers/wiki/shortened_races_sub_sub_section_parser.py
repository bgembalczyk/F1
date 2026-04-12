from typing import Any

from scrapers.mixins.apply_for_elements import ApplyForElementsMixin
from scrapers.parsers.table.points import ShortenedRacesPointsTableMapper
from scrapers.parsers.wiki.sublevels.sub_sub_section import SubSubSectionParser


class ShortenedRacesSubSubSectionParser(ApplyForElementsMixin, SubSubSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self._table_parser = ShortenedRacesPointsTableMapper()

    def collect_rows(self, parsed: dict[str, Any]) -> list[dict[str, Any]]:
        return self._table_parser.collect_rows(parsed)

    def _parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        parsed = super()._parse_group(elements, context=context)
        self.apply_table_mapper(parsed)
        return parsed

