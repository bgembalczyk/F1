from __future__ import annotations

from typing import Any

from scrapers.base.helpers.tables.lap_records import LapRecordsTableScraper
from scrapers.base.options import ScraperOptions
from scrapers.base.table.table_parser_registry import TableParserRegistry
from scrapers.circuits.helpers.lap_record import collect_lap_records
from scrapers.circuits.helpers.layout import detect_layout_name
from scrapers.circuits.postprocess.assembler import CircuitRecordAssembler
from scrapers.circuits.postprocess.assembler import CircuitRecordDTO
from scrapers.circuits.sections.lap_records_table_classifier import (
    CircuitLapRecordsTableClassifier,
)
from scrapers.wiki.parsers.elements.article_tables import ArticleTablesParser


class DomainRecordService:
    def __init__(
        self,
        *,
        assembler: CircuitRecordAssembler | None = None,
        article_tables_parser: ArticleTablesParser | None = None,
        lap_records_classifier: CircuitLapRecordsTableClassifier | None = None,
    ) -> None:
        self._assembler = assembler or CircuitRecordAssembler()
        self._article_tables_parser = article_tables_parser or ArticleTablesParser(
            include_source_table=True,
        )
        self._lap_records_classifier = (
            lap_records_classifier or CircuitLapRecordsTableClassifier()
        )
        self._lap_records_registry = TableParserRegistry()
        self._lap_records_registry.register(
            "lap_records",
            self._collect_lap_records_from_table,
        )

    def collect_lap_record_rows(
        self,
        *,
        soup: Any,
        url: str,
        include_urls: bool,
        fetcher: Any,
        policy: Any,
        debug_dir: str | None,
    ) -> list[dict[str, Any]]:
        lap_scraper = LapRecordsTableScraper(
            options=ScraperOptions(
                include_urls=include_urls,
                fetcher=fetcher,
                policy=policy,
                debug_dir=debug_dir,
            ),
        )
        lap_scraper.url = url
        all_records: list[dict[str, Any]] = []

        for table_data in self._article_tables_parser.parse(soup):
            table = table_data.get("_table")
            if table is None:
                continue

            table_type = self._lap_records_classifier.classify(
                table_data,
                lap_scraper=lap_scraper,
            )
            if table_type is None:
                continue

            records = self._lap_records_registry.parse(
                table_type,
                table_data=table_data,
                lap_scraper=lap_scraper,
            )
            all_records.extend(records)

        return all_records

    def _collect_lap_records_from_table(
        self,
        *,
        table_data: dict[str, Any],
        lap_scraper: LapRecordsTableScraper,
    ) -> list[dict[str, Any]]:
        table = table_data.get("_table")
        headers = table_data.get("headers")
        if table is None or not isinstance(headers, list):
            return []

        base_layout = detect_layout_name(table, headers)
        return collect_lap_records(table, headers, base_layout, lap_scraper)

    def assemble_record(
        self,
        *,
        source_url: str,
        infobox: dict[str, Any],
        lap_record_rows: list[dict[str, Any]],
        sections: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return self._assembler.assemble(
            payload=CircuitRecordDTO(
                url=source_url,
                infobox=infobox,
                lap_record_rows=lap_record_rows,
                sections=sections,
            ),
        )
