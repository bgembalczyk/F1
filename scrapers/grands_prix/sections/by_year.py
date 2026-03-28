from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from scrapers.base.factory.record_factory import RECORD_FACTORIES
from scrapers.base.sections.interface import SectionParseResult
from scrapers.base.sections.serializer import build_section_metadata
from scrapers.base.table.columns.types import AutoColumn
from scrapers.base.table.columns.types import UrlColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.base.table.parser import HtmlTableParser
from scrapers.base.table.pipeline import TablePipeline
from scrapers.grands_prix.assemblers.by_year import GrandPrixByYearRecordAssembler
from scrapers.grands_prix.columns.circuit_location import LocationColumn
from scrapers.grands_prix.columns.constructor_split import ConstructorSplitColumn
from scrapers.grands_prix.columns.driver_list import DriverListColumn

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


class GrandPrixByYearSectionParser:
    def __init__(
        self,
        *,
        url: str,
        include_urls: bool,
        normalize_empty_values: bool,
        assembler: GrandPrixByYearRecordAssembler | None = None,
    ) -> None:
        self._url = url
        self._include_urls = include_urls
        self._normalize_empty_values = normalize_empty_values
        self._assembler = assembler or GrandPrixByYearRecordAssembler()

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        pipeline = self._build_pipeline(section_id=None)
        parser = HtmlTableParser(
            section_id=None,
            expected_headers=pipeline.expected_headers,
            section_domain="grands_prix",
        )
        records: list[dict[str, Any]] = []
        for row_index, row in enumerate(parser.parse(section_fragment)):
            parsed_record = pipeline.parse_cells(
                row.headers,
                row.cells,
                row_index=row_index,
            )
            if not parsed_record:
                continue
            assembled_record = self._assembler.assemble(
                record=parsed_record,
                row=row.raw_tr,
            )
            if assembled_record is not None:
                records.append(assembled_record)
        return SectionParseResult(
            section_id="By_year",
            section_label="By year",
            records=records,
            metadata=build_section_metadata(
                parser=self.__class__.__name__,
                source="wikipedia",
            ),
        )

    def _build_pipeline(self, section_id: str | None) -> TablePipeline:
        schema = TableSchemaDSL(
            columns=[
                column("Year", "year", UrlColumn()),
                column("Driver", "driver", DriverListColumn()),
                column("Constructor", "constructor", ConstructorSplitColumn()),
                column("Report", "report", AutoColumn()),
                column("Location", "location", LocationColumn()),
            ],
        )
        config = ScraperConfig(
            url=self._url,
            section_id=section_id,
            expected_headers=["Year", "Driver", "Constructor", "Report"],
            schema=schema,
            record_factory=RECORD_FACTORIES.mapping(),
        )
        return TablePipeline(
            config=config,
            include_urls=self._include_urls,
            normalize_empty_values=self._normalize_empty_values,
        )
