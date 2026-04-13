from __future__ import annotations

from typing import Any

from bs4 import BeautifulSoup

from scrapers.mappers.mapper_abc import MapperABC
from scrapers.parsers.section.table.base import TableSectionParser
from scrapers.section.parse_results import SectionParseResult


class CircuitEventsTableRecordMapper(MapperABC[dict[str, Any], dict[str, Any] | None]):
    def map(
        self,
        table_data: dict[str, Any],
        table_classification: dict[str, Any],
        table_pipeline: Any,
    ) -> dict[str, Any]:
        _ = table_data
        _ = table_pipeline
        return table_classification


class CircuitEventsSectionParser(TableSectionParser):
    def __init__(self) -> None:
        super().__init__(
            section_id="events",
            section_label="Events",
            mapper=CircuitEventsTableRecordMapper(),
        )

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        return super().parse(section_fragment)
