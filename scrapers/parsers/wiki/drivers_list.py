from typing import Any

from bs4 import BeautifulSoup

from scrapers.parsers.table.drivers_list import DriversListTableMapper
from scrapers.parsers.section.extraction_context import SectionExtractionContext
from scrapers.parsers.wiki.nested_wiki import NestedWikiSectionParser


class DriversListSectionParser(NestedWikiSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self._table_parser = DriversListTableMapper()

    def parse(
        self,
        element: BeautifulSoup,
        *,
        context: SectionExtractionContext | None = None,
    ) -> dict[str, Any]:
        parsed = super().parse(element, context=context)
        self._apply_drivers_table_parser(parsed)
        return parsed

    def _parse_group(
        self,
        elements: list,
        *,
        context: SectionExtractionContext | None = None,
    ) -> dict[str, Any]:
        parsed = super()._parse_group(elements, context=context)
        self._apply_drivers_table_parser(parsed)
        return parsed

    def _apply_drivers_table_parser(self, payload: dict[str, Any]) -> None:
        for section in payload.get("sub_sections", []):
            self._apply_for_elements(section.get("elements", []))
            self._apply_drivers_table_parser(section)

    def _apply_for_elements(self, elements: list[dict[str, Any]]) -> None:
        for element in elements:
            if element.get("kind") != "table":
                continue
            data = element.get("data")
            if not isinstance(data, dict):
                continue
            parsed = self._table_parser.map(data)
            if parsed is not None:
                element["data"] = parsed
