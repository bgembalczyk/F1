from __future__ import annotations

from typing import Any

from scrapers.parsers.section.table.base import TableSectionParser
from scrapers.parsers.section.table.contracts import SectionTableRecordMapperABC


class CircuitEventsTableRecordMapper(SectionTableRecordMapperABC[dict[str, Any], Any]):
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
