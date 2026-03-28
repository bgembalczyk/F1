from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from bs4 import Tag

from scrapers.circuits.helpers.lap_record import is_lap_record_table

if TYPE_CHECKING:
    from scrapers.base.helpers.tables.lap_records import LapRecordsTableScraper


class CircuitLapRecordsTableClassifier:
    def classify(
        self,
        table_data: dict[str, Any],
        *,
        lap_scraper: LapRecordsTableScraper,
    ) -> str | None:
        table = table_data.get("_table")
        headers = table_data.get("headers")
        if not isinstance(table, Tag) or not isinstance(headers, list):
            return None

        table_type = table_data.get("table_type")
        if table_type == "lap_records" or is_lap_record_table(headers, lap_scraper):
            return "lap_records"
        return None
