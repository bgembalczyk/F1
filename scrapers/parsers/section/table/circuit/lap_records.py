from __future__ import annotations

from typing import Any

from bs4 import Tag

from scrapers.helpers.lap_record import collect_lap_records
from scrapers.helpers.lap_record import is_lap_record_table
from scrapers.helpers.layout import detect_layout_name
from scrapers.lap_records_table import LapRecordsTableScraper
from scrapers.options import ScraperOptions
from scrapers.parsers.section.table.base import TableSectionParser
from scrapers.parsers.section.table.contracts import SectionTableClassifierABC
from scrapers.parsers.section.table.contracts import SectionTableRecordMapperABC


class CircuitLapRecordsTableClassifier(SectionTableClassifierABC[tuple[Tag, list[str]]]):
    def __init__(self, *, options: ScraperOptions, url: str) -> None:
        self._options = options
        self._url = url

    def classify(self, table_data: dict[str, Any]) -> tuple[Tag, list[str]] | None:
        table = table_data.get("_table")
        headers = table_data.get("headers")
        if not isinstance(table, Tag) or not isinstance(headers, list):
            return None

        lap_scraper = self._build_lap_scraper()
        if not is_lap_record_table(headers, lap_scraper):
            return None
        return table, headers

    def _build_lap_scraper(self) -> LapRecordsTableScraper:
        lap_scraper = LapRecordsTableScraper(options=self._options)
        lap_scraper.url = self._url
        return lap_scraper


class CircuitLapRecordsTableRecordMapper(
    SectionTableRecordMapperABC[tuple[Tag, list[str]], Any],
):
    def __init__(self, *, options: ScraperOptions, url: str) -> None:
        self._options = options
        self._url = url

    def map(
        self,
        table_data: dict[str, Any],
        table_classification: tuple[Tag, list[str]],
        table_pipeline: Any,
    ) -> dict[str, Any]:
        _ = table_data
        _ = table_pipeline
        table, headers = table_classification
        layout = detect_layout_name(table, headers)
        lap_scraper = self._build_lap_scraper()
        return {
            "layout": layout,
            "rows": collect_lap_records(table, headers, layout, lap_scraper),
        }

    def _build_lap_scraper(self) -> LapRecordsTableScraper:
        lap_scraper = LapRecordsTableScraper(options=self._options)
        lap_scraper.url = self._url
        return lap_scraper


class CircuitLapRecordsSectionParser(TableSectionParser):
    def __init__(self, *, options: ScraperOptions, url: str) -> None:
        super().__init__(
            section_id="lap_records",
            section_label="Lap records",
            include_source_table=True,
            classifier=CircuitLapRecordsTableClassifier(options=options, url=url),
            mapper=CircuitLapRecordsTableRecordMapper(options=options, url=url),
        )

    def build_result(self, records: list[dict[str, Any]]):
        flattened: list[dict[str, Any]] = []
        for record in records:
            flattened.extend(record.get("rows", []))
        return super().build_result(flattened)
