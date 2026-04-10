from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any

from scrapers.contracts import RecordAssemblerProtocol
from scrapers.helpers.lap_record import collect_lap_records
from scrapers.helpers.lap_record import is_lap_record_table
from scrapers.helpers.layout import detect_layout_name
from scrapers.lap_records_table import LapRecordsTableScraper
from scrapers.options import ScraperOptions
from scrapers.records.DTO.circuit import CircuitRecordDTO
from scrapers.records.assemblers.circuit import CircuitRecordAssembler
from scrapers.services.domain_record._shared import DomainRecordResult
from scrapers.wiki.parsers.elements.article_tables import ArticleTablesParser


@dataclass(frozen=True, slots=True)
class CircuitDomainRecordInput:
    source_url: str
    soup: Any
    infobox: dict[str, Any]
    sections: list[dict[str, Any]]
    include_urls: bool
    fetcher: Any
    policy: Any
    debug_dir: str | None


class DomainRecordService:
    def __init__(
        self,
        *,
        assembler: RecordAssemblerProtocol[CircuitRecordDTO] | None = None,
        article_tables_parser: ArticleTablesParser | None = None,
    ) -> None:
        self._assembler = assembler or CircuitRecordAssembler()
        self._article_tables_parser = article_tables_parser or ArticleTablesParser(
            include_source_table=True,
        )

    def execute(self, payload: CircuitDomainRecordInput) -> DomainRecordResult:
        return DomainRecordResult(
            record=self._assembler.assemble(
                CircuitRecordDTO(
                    url=payload.source_url,
                    infobox=payload.infobox,
                    lap_record_rows=self._collect_lap_record_rows(payload),
                    sections=payload.sections,
                ),
            ),
        )

    def _collect_lap_record_rows(
        self,
        payload: CircuitDomainRecordInput,
    ) -> list[dict[str, Any]]:
        lap_scraper = LapRecordsTableScraper(
            options=ScraperOptions(
                include_urls=payload.include_urls,
                fetcher=payload.fetcher,
                policy=payload.policy,
                debug_dir=payload.debug_dir,
            ),
        )
        lap_scraper.url = payload.source_url
        all_records: list[dict[str, Any]] = []

        for table_data in self._article_tables_parser.parse(payload.soup):
            table = table_data.get("_table")
            if table is None:
                continue

            headers = table_data["headers"]
            table_type = table_data.get("table_type")
            if table_type != "lap_records" and not is_lap_record_table(
                headers,
                lap_scraper,
            ):
                continue

            base_layout = detect_layout_name(table, headers)
            all_records.extend(
                collect_lap_records(table, headers, base_layout, lap_scraper),
            )

        return all_records
