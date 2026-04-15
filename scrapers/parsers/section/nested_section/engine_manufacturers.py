from typing import Any

from scrapers.parsers.engine_manufacturers_table_mapper import (
    EngineManufacturersTableMapper,
)
from scrapers.parsers.section.sub_section.engine_manufacturers_indianapolis import (
    EngineManufacturersIndianapolisSubSectionParser,
)
from scrapers.parsers.wiki.recursive import RecursiveSectionParser


class EngineManufacturersSectionParser(RecursiveSectionParser):
    heading_class = "mw-heading3"
    output_key = "sub_sections"

    def __init__(self) -> None:
        super().__init__(child_parser=EngineManufacturersIndianapolisSubSectionParser())
        self._table_mapper = EngineManufacturersTableMapper()

    def _parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        parsed = super()._parse_group(elements, context=context)
        self._apply_engine_table_parser(parsed)
        return parsed

    def _apply_engine_table_parser(self, payload: dict[str, Any]) -> None:
        self._apply_for_elements(payload.get("elements", []))
        for value in payload.values():
            if isinstance(value, dict):
                self._apply_engine_table_parser(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self._apply_engine_table_parser(item)
