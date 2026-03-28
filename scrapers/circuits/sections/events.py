from __future__ import annotations

from typing import Any

from scrapers.base.sections.section_table_parser_base import SectionTableParserBase


class CircuitEventsSectionParser(SectionTableParserBase):
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
