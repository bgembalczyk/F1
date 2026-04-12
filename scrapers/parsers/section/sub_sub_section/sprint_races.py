from typing import Any

from bs4 import Tag

from scrapers.mixins.apply_for_elements import ApplyForElementsMixin
from scrapers.parsers.section.extraction_context import SectionExtractionContext
from scrapers.sprint_points_table_mapper import SprintPointsTableMapper
from scrapers.parsers.section.sub_sub_section.base import SubSubSectionParser


class SprintRacesSubSubSectionParser(ApplyForElementsMixin, SubSubSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self._table_parser = SprintPointsTableMapper()

    def parse(
        self,
        element: Tag | list[Tag],
        *,
        context: SectionExtractionContext | None = None,
    ) -> dict[str, object]:
        return super().parse(element, context=context)

    def collect_rows(self, parsed: dict[str, Any]) -> list[dict[str, Any]]:
        return self._table_parser.collect_rows(parsed)

    def _parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        parsed = super()._parse_group(elements, context=context)
        if not parsed.get("sub_sub_sub_sections"):
            parsed = self.child_parser.parse(elements, context=context)
        self.apply_table_mapper(parsed)
        return parsed
