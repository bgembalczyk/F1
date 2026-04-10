from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any

from scrapers.helpers.lap_record import collect_lap_records
from scrapers.helpers.lap_record import is_lap_record_table
from scrapers.helpers.layout import detect_layout_name
from scrapers.lap_records_table import LapRecordsTableScraper
from scrapers.options import ScraperOptions
from scrapers.records.dto.circuit import CircuitRecordDTO
from scrapers.records.assemblers.circuit import CircuitRecordAssembler
from scrapers.services.domain_record.base_adapter import BaseAssemblerPipelineService
from scrapers.wiki.parsers.elements.article_tables import ArticleTablesParser

if TYPE_CHECKING:
    from scrapers.contracts import RecordAssemblerProtocol


@dataclass(frozen=True, slots=True)
class CircuitDomainRecordInput:
    source_url: str
    infobox: dict[str, Any]
    lap_record_rows: list[dict[str, Any]]
    sections: list[dict[str, Any]]


class CircuitPipelineService(
    BaseAssemblerPipelineService[CircuitDomainRecordInput, CircuitRecordDTO],
):
    required_fields = ("source_url", "infobox", "lap_record_rows", "sections")

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

    def _validate_input(self, input_dto: CircuitDomainRecordInput) -> None:
        self.validate_required(
            {
                "source_url": input_dto.source_url,
                "infobox": input_dto.infobox,
                "lap_record_rows": input_dto.lap_record_rows,
                "sections": input_dto.sections,
            },
            self.required_fields,
        )

    def build_payload(self, input_dto: CircuitDomainRecordInput) -> CircuitRecordDTO:
        return CircuitRecordDTO(
            url=input_dto.source_url,
            infobox=dict(input_dto.infobox),
            lap_record_rows=list(input_dto.lap_record_rows),
            sections=list(input_dto.sections),
        )

    def assemble(self, payload: CircuitRecordDTO) -> dict[str, Any]:
        return self._assembler.assemble(payload)

    def _compat_input_from_source(self, source: dict[str, Any]) -> CircuitDomainRecordInput:
        return CircuitDomainRecordInput(
            source_url=str(source["source_url"]),
            infobox=dict(source["infobox"]),
            lap_record_rows=list(source["lap_record_rows"]),
            sections=list(source["sections"]),
        )
