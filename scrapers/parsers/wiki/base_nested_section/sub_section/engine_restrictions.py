from typing import Any

from bs4 import Tag

from scrapers.mixins.apply_for_elements import ApplyForElementsMixin
from scrapers.parsers.engine_restrictions_table_mapper import EngineRestrictionsTableMapper
from scrapers.parsers.section.extraction_context import SectionExtractionContext
from scrapers.parsers.wiki.base_nested_section.sub_section.base import SubSectionParser


class EngineSubSectionParser(ApplyForElementsMixin, SubSectionParser):
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

