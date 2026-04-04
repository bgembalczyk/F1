from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from bs4 import Tag

from scrapers.base.factory.record_factory import MappingRecordFactory
from scrapers.base.helpers.table_parsing import TableParsingHelper
from scrapers.base.sections.section_table_parser_base import SectionTableParserBase
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

if TYPE_CHECKING:
    from scrapers.base.options import ScraperOptions
    from scrapers.base.table.dsl.table_schema import TableSchemaDSL


class DriverResultsSectionParser(SectionTableParserBase):
    def __init__(
        self,
        *,
        url: str,
        options: ScraperOptions,
        classifier: DriverResultsTableClassifier | None = None,
        schema_factory: DriverResultsSchemaFactory | None = None,
    ) -> None:
        super().__init__(
            section_id="driver_results",
            section_label="Driver results",
            include_heading_path=True,
            include_source_table=True,
        )
        self._url = url
        self._options = options
        self._classifier = classifier or DriverResultsTableClassifier()
        self._schema_factory = schema_factory or DriverResultsSchemaFactory(
            unknown_value=UNKNOWN_VALUE,
        )

    def classify_table(self, table_data: dict[str, Any]) -> str | None:
        headers = table_data.get("headers")
        table = table_data.get("_table")
        if not isinstance(headers, list) or not isinstance(table, Tag):
            return None
        return self._classifier.classify(headers)

    def build_pipeline(
        self,
        *,
        table_data: dict[str, Any],
        table_classification: str,
    ) -> TablePipeline:
        schema = self._schema_factory.build(
            table_type=table_classification,
            headers=table_data.get("headers", []),
        )
        return self._build_pipeline(schema=schema)

    def map_table_result(
        self,
        *,
        table_data: dict[str, Any],
        table_classification: str,
        table_pipeline: TablePipeline,
    ) -> dict[str, Any] | None:
        table = table_data.get("_table")
        headers = table_data.get("headers")
        if not isinstance(table, Tag) or not isinstance(headers, list):
            return None

        parsed: dict[str, Any] = {
            "table_type": table_classification,
            "headers": headers,
            "rows": self._parse_table(table, table_pipeline),
        }
        heading_path = table_data.get("heading_path")
        if heading_path is not None:
            parsed["heading_path"] = heading_path
        return parsed

    def _parse_table(self, table: Tag, pipeline: TablePipeline) -> list[dict[str, Any]]:
        return TableParsingHelper.parse_table_with_pipeline(table, pipeline)

    def _build_pipeline(self, *, schema: TableSchemaDSL) -> TablePipeline:
        config = ScraperConfig(
            url=self._url,
            section_id=None,
            expected_headers=None,
            schema=schema,
            default_column=AutoColumn(),
            record_factory=MappingRecordFactory(),
        )
        return TablePipeline(
            config=config,
            include_urls=self._options.include_urls,
            normalize_empty_values=self._options.normalize_empty_values,
            debug_dir=self._options.debug_dir,
        )
