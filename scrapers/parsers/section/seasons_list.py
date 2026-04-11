from typing import Any

from scrapers.parsers.section.base import BaseSectionParser
from scrapers.mixins.apply_for_elements import ApplyForElementsMixin
from scrapers.parsers.section.nested.nested_wiki import NestedWikiSectionParser
from scrapers.parsers.table.seasons_list import SeasonsTableParser


class SeasonsSectionParser(BaseSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self._table_parser = SeasonsTableParser()

    def _parse_group(
        self,
        elements: list,
        *,
        context=None,
    ) -> dict[str, Any]:
        parsed = super()._parse_group(elements, context=context)
        self._apply_seasons_table_parser(parsed)
        return parsed

    def _apply_seasons_table_parser(self, payload: dict[str, Any]) -> None:
        for section in payload.get("sub_sections", []):
            self._apply_for_elements(section.get("elements", []))
            self._apply_seasons_table_parser(section)

    def _apply_for_elements(self, elements: list[dict[str, Any]]) -> None:
        for element in elements:
            if element.get("kind") != "table":
                continue
            data = element.get("data")
            if not isinstance(data, dict):
                continue
            parsed = self._table_parser.parse(data)
            if parsed is not None:
                element["data"] = parsed
