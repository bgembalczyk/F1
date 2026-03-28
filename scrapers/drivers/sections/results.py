from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.helpers.table_parsing import TableParsingHelper
from scrapers.base.records import record_from_mapping
from scrapers.base.sections.interface import SectionParseResult
from scrapers.base.sections.serializer import build_section_metadata
from scrapers.base.table.columns.types import AutoColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.pipeline import TablePipeline
from scrapers.drivers.sections.constants import UNKNOWN_VALUE
from scrapers.drivers.sections.driver_results_schema_factory import (
    DriverResultsSchemaFactory,
)
from scrapers.drivers.sections.driver_results_table_classifier import (
    DriverResultsTableClassifier,
)
from scrapers.wiki.parsers.elements.article_tables import ArticleTablesParser

if TYPE_CHECKING:
    from scrapers.base.options import ScraperOptions
    from scrapers.base.table.dsl.table_schema import TableSchemaDSL


class DriverResultsSectionParser:
    def __init__(
        self,
        *,
        url: str,
        options: ScraperOptions,
        classifier: DriverResultsTableClassifier | None = None,
        schema_factory: DriverResultsSchemaFactory | None = None,
    ) -> None:
        self._url = url
        self._options = options
        self._table_parser = ArticleTablesParser(
            include_heading_path=True,
            include_source_table=True,
        )
        self._classifier = classifier or DriverResultsTableClassifier()
        self._schema_factory = schema_factory or DriverResultsSchemaFactory(
            unknown_value=UNKNOWN_VALUE,
        )

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        records: list[dict[str, Any]] = []
        for table_data in self._table_parser.parse(section_fragment):
            parsed = self._parse_results_table_data(table_data)
            if parsed is None:
                continue
            if "heading_path" in table_data:
                parsed["heading_path"] = table_data["heading_path"]
            records.append(parsed)
        return SectionParseResult(
            section_id="driver_results",
            section_label="Driver results",
            records=records,
            metadata=build_section_metadata(parser=self.__class__.__name__, source="wikipedia"),
        )

    def _parse_results_table_data(
        self,
        table_data: dict[str, Any],
    ) -> dict[str, Any] | None:
        headers = table_data.get("headers", [])
        table = table_data.get("_table")
        if not headers or not isinstance(table, Tag):
            return None

        table_type = self._classifier.classify(headers)
        if table_type is None:
            return None

        schema = self._schema_factory.build(table_type=table_type, headers=headers)
        return {
            "table_type": table_type,
            "headers": headers,
            "rows": self._parse_table(table, self._build_pipeline(schema=schema)),
        }

    def _parse_table(self, table: Tag, pipeline: TablePipeline) -> list[dict[str, Any]]:
        return TableParsingHelper.parse_table_with_pipeline(table, pipeline)

    def _build_pipeline(self, *, schema: TableSchemaDSL) -> TablePipeline:
        config = ScraperConfig(
            url=self._url,
            section_id=None,
            expected_headers=None,
            schema=schema,
            default_column=AutoColumn(),
            record_factory=record_from_mapping,
        )
        return TablePipeline(
            config=config,
            include_urls=self._options.include_urls,
            normalize_empty_values=self._options.normalize_empty_values,
            debug_dir=self._options.debug_dir,
        )
