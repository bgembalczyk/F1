from typing import Any

from bs4 import Tag

from scrapers.mixins.apply_for_elements import ApplyForElementsMixin
from scrapers.parsers.section.extraction_context import SectionExtractionContext
from scrapers.parsers.engine_manufacturers_table_mapper import EngineManufacturersTableMapper
from scrapers.parsers.section.nested_section.base import NestedWikiSectionParser
from scrapers.parsers.section.sub_section.engine_manufacturers_indianapolis import EngineManufacturersIndianapolisSubSectionParser


class EngineManufacturersSectionParser(ApplyForElementsMixin, NestedWikiSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self.child_parser = EngineManufacturersIndianapolisSubSectionParser()
        self._table_mapper = EngineManufacturersTableMapper()

    def parse(
        self,
        element: Tag | list[Tag],
        *,
        context: SectionExtractionContext | None = None,
    ) -> dict[str, object]:
        return super().parse(element, context=context)

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
