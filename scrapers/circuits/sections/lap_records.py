from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from bs4 import Tag

from scrapers.base.helpers.tables.lap_records import LapRecordsTableScraper
from scrapers.base.sections.section_table_parser_base import SectionTableParserBase
from scrapers.base.table.table_parser_registry import TableParserRegistry
from scrapers.circuits.helpers.lap_record import collect_lap_records
from scrapers.circuits.helpers.layout import detect_layout_name
from scrapers.circuits.sections.lap_records_table_classifier import (
    CircuitLapRecordsTableClassifier,
)

if TYPE_CHECKING:
    from scrapers.base.options import ScraperOptions


class CircuitLapRecordsSectionParser(SectionTableParserBase):
    def __init__(
        self,
        *,
        options: ScraperOptions,
        url: str,
        classifier: CircuitLapRecordsTableClassifier | None = None,
    ) -> None:
        super().__init__(
            section_id="lap_records",
            section_label="Lap records",
            include_source_table=True,
        )
        self._options = options
        self._url = url
        self._classifier = classifier or CircuitLapRecordsTableClassifier()
        self._parser_registry = TableParserRegistry()
        self._parser_registry.register("lap_records", self._parse_lap_records_table)

    def classify_table(self, table_data: dict[str, Any]) -> str | None:
        lap_scraper = self._build_lap_scraper()
        return self._classifier.classify(table_data, lap_scraper=lap_scraper)

    def map_table_result(
        self,
        *,
        table_data: dict[str, Any],
        table_classification: str,
        table_pipeline: Any,
    ) -> dict[str, Any] | None:
        lap_scraper = self._build_lap_scraper()
        return self._parser_registry.parse(
            table_classification,
            table_data=table_data,
            lap_scraper=lap_scraper,
        )

    def _parse_lap_records_table(
        self,
        *,
        table_data: dict[str, Any],
        lap_scraper: LapRecordsTableScraper,
    ) -> dict[str, Any] | None:
        table = table_data.get("_table")
        headers = table_data.get("headers")
        if not isinstance(table, Tag) or not isinstance(headers, list):
            return None
        layout = detect_layout_name(table, headers)
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
