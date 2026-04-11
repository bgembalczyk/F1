from typing import Any

from bs4 import BeautifulSoup

from scrapers.parsers.section.extraction_context import SectionExtractionContext
from scrapers.parsers.section.nested_wiki import NestedWikiSectionParser
from scrapers.parsers.table.seasons_list import SeasonsTableParser


class SeasonsSectionParser(NestedWikiSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self._table_parser = SeasonsTableParser()

    def parse(
        self,
        element: BeautifulSoup,
        *,
        context: SectionExtractionContext | None = None,
    ) -> dict[str, Any]:
        parsed = super().parse(element, context=context)
        self._apply_seasons_table_parser(parsed)
        return parsed

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
