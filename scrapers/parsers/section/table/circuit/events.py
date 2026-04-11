from __future__ import annotations

from typing import Any

from scrapers.parsers.section.table.base import TableSectionParser


class CircuitEventsSectionParser(TableSectionParser):
    def __init__(self) -> None:
        super().__init__(section_id="events", section_label="Events")

    def map_table_result(
        self,
        *,
        _table_data: dict[str, Any],
        table_classification: dict[str, Any],
        _table_pipeline: Any,
    ) -> dict[str, Any]:
        return table_classification
