from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from bs4 import Tag

from scrapers.base.helpers.tables.lap_records import LapRecordsTableScraper
from scrapers.base.sections.section_table_parser_base import SectionTableParserBase
from scrapers.circuits.helpers.lap_record import collect_lap_records
from scrapers.circuits.helpers.lap_record import is_lap_record_table
from scrapers.circuits.helpers.layout import detect_layout_name

if TYPE_CHECKING:
    from scrapers.base.options import ScraperOptions


class CircuitLapRecordsSectionParser(SectionTableParserBase):
    def __init__(self, *, options: ScraperOptions, url: str) -> None:
        super().__init__(
            section_id="lap_records",
            section_label="Lap records",
            include_source_table=True,
        )
        self._options = options
        self._url = url

    def classify_table(
        self,
        table_data: dict[str, Any],
    ) -> tuple[Tag, list[str]] | None:
        table = table_data.get("_table")
        headers = table_data.get("headers")
        if not isinstance(table, Tag) or not isinstance(headers, list):
            return None

        lap_scraper = self._build_lap_scraper()
        if not is_lap_record_table(headers, lap_scraper):
            return None
        return table, headers

    def map_table_result(
        self,
        *,
        table_data: dict[str, Any],
        table_classification: tuple[Tag, list[str]],
        table_pipeline: Any,
    ) -> dict[str, Any]:
        table, headers = table_classification
        layout = detect_layout_name(table, headers)
        lap_scraper = self._build_lap_scraper()
        return {
            "layout": layout,
            "rows": collect_lap_records(table, headers, layout, lap_scraper),
        }

    def build_result(self, records: list[dict[str, Any]]):
        flattened: list[dict[str, Any]] = []
        for record in records:
            flattened.extend(record.get("rows", []))
        return super().build_result(flattened)

    def _build_lap_scraper(self) -> LapRecordsTableScraper:
        lap_scraper = LapRecordsTableScraper(options=self._options)
        lap_scraper.url = self._url
        return lap_scraper
