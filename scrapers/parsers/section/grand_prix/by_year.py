from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from models.records.factories.mapping import MappingRecordFactory
from scrapers.assemblers import GrandPrixByYearRecordAssembler
from scrapers.columns.spec import ColumnSpec
from scrapers.columns.types.auto import AutoColumn
from scrapers.columns.types.driver_list import DriverListColumn
from scrapers.columns.types.function.circuit_location import LocationColumn
from scrapers.columns.types.multi.constructor_split import ConstructorSplitColumn
from scrapers.columns.types.url import UrlColumn
from scrapers.configs.public import TableConfig
from scrapers.parsers.table.html import HtmlTableParser
from scrapers.parsers.section.base_section_parser import BaseSectionParser
from scrapers.pipeline_table import TablePipeline
from scrapers.section.parse_results import SectionParseResult
from scrapers.section.serializer import build_section_metadata
from scrapers.table_schema_dsl import TableSchemaDSL

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


class GrandPrixByYearSectionParser(BaseSectionParser):
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

    def parse(self, fragment: BeautifulSoup) -> SectionParseResult:
        pipeline = self._build_pipeline(section_id=None)
        parser = HtmlTableParser(
            section_id=None,
            expected_headers=pipeline.expected_headers,
            section_domain="grands_prix",
        )
        records: list[dict[str, Any]] = []
        for row_index, row in enumerate(parser.parse(fragment)):
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
                ColumnSpec("Year", "year", UrlColumn()),
                ColumnSpec("Driver", "driver", DriverListColumn()),
                ColumnSpec("Constructor", "constructor", ConstructorSplitColumn()),
                ColumnSpec("Report", "report", AutoColumn()),
                ColumnSpec("Location", "location", LocationColumn()),
            ],
        )
        config = TableConfig(
            url=self._url,
            section_id=section_id,
            expected_headers=["Year", "Driver", "Constructor", "Report"],
            schema=schema,
            record_factory=MappingRecordFactory(),
        )
        return TablePipeline(
            config=config,
            include_urls=self._include_urls,
            normalize_empty_values=self._normalize_empty_values,
        )
