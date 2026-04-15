from typing import Any

from bs4 import Tag

from scrapers.parsers.engine_restrictions_table_mapper import (
    EngineRestrictionsTableMapper,
)
from scrapers.parsers.section.extraction_context import SectionExtractionContext
from scrapers.parsers.wiki.recursive import RecursiveSectionParser


class EngineSubSectionParser(RecursiveSectionParser):
    heading_class = "mw-heading4"
    output_key = "sub_sub_sections"

    def __init__(self) -> None:
        super().__init__()
        self._table_mapper = EngineRestrictionsTableMapper()

    def parse(
        self,
        element: Tag | list[Tag],
        *,
        context: SectionExtractionContext | None = None,
    ) -> dict[str, object]:
        return super().parse(element, context=context)

    def _parse_group(
        self,
        elements: list,
        *,
        context=None,
    ) -> dict[str, Any]:
        parsed = super()._parse_group(elements, context=context)
        for section in parsed.get("sub_sub_sections", []):
            self._table_mapper.apply_to_payload(section)
        return parsed

    def _apply_engine_restrictions_table_parser(self, payload: dict[str, Any]) -> None:
        for section in payload.get("sub_sub_sections", []):
            self._apply_for_elements(section.get("elements", []))
            self._apply_engine_restrictions_table_parser(section)
