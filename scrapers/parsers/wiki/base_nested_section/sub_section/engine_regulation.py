from typing import Any

from bs4 import Tag

from scrapers.parsers.engine_regulation_table_mapper import EngineRegulationTableMapper
from scrapers.parsers.section.extraction_context import SectionExtractionContext
from scrapers.parsers.wiki.base_nested_section.sub_section.base import SubSectionParser


class EngineRegulationSubSectionParser(SubSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self._table_mapper = EngineRegulationTableMapper()

    def parse(
        self,
        element: Tag | list[Tag],
        *,
        context: SectionExtractionContext | None = None,
    ) -> dict[str, object]:
        return super().parse(element, context=context)

    def _parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        parsed = super()._parse_group(elements, context=context)
        self._apply_engine_regulation_table_parser(parsed)
        return parsed

    def _apply_engine_regulation_table_parser(self, payload: dict[str, Any]) -> None:
        for section in payload.get("sub_sub_sections", []):
            self._apply_for_elements(section.get("elements", []))
            self._apply_engine_regulation_table_parser(section)

    def parse_group(self, sections: list[dict[str, Any]], *, context: Any = None) -> dict[str, Any]:
        payload: dict[str, Any] = {"sub_sub_sections": sections}
        self._apply_engine_regulation_table_parser(payload)
        return payload

    def _apply_for_elements(self, elements: list[dict[str, Any]]) -> None:
        for element in elements:
            if element.get("kind") != "table":
                continue
            data = element.get("data")
            if not isinstance(data, dict):
                continue
            parsed = self._table_mapper.map(data)
            if parsed is not None:
                element["data"] = parsed

