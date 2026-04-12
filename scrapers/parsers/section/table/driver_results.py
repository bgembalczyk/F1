from __future__ import annotations

from typing import Any

from bs4 import Tag

from models.records.factories.mapping import MappingRecordFactory
from scrapers.columns.types.auto import AutoColumn
from scrapers.configs.public import TableConfig
from scrapers.driver_results_schema_factory import DriverResultsSchemaFactory
from scrapers.driver_results_table_classifier import DriverResultsTableClassifier
from scrapers.options import ScraperOptions
from scrapers.parsers.section.table.base import TableSectionParser
from scrapers.parsers.section.table.contracts import SectionTableClassifierABC
from scrapers.parsers.section.table.contracts import SectionTableRecordMapperABC
from scrapers.pipeline_table import TablePipeline
from scrapers.section.constants import UNKNOWN_VALUE
from scrapers.table_parsing_helper import TableParsingHelper
from scrapers.table_schema_dsl import TableSchemaDSL


class DriverResultsSectionTableClassifier(SectionTableClassifierABC[str]):
    def __init__(self, classifier: DriverResultsTableClassifier | None = None) -> None:
        self._classifier = classifier or DriverResultsTableClassifier()

    def classify(self, table_data: dict[str, Any]) -> str | None:
        headers = table_data.get("headers")
        table = table_data.get("_table")
        if not isinstance(headers, list) or not isinstance(table, Tag):
            return None
        return self._classifier.classify(headers)


class DriverResultsTableRecordMapper(SectionTableRecordMapperABC[str, TablePipeline]):
    def map(
        self,
        raw: dict[str, Any],
        *,
        table_classification: str,
        table_pipeline: TablePipeline,
    ) -> dict[str, Any] | None:
        table = raw.get("_table")
        headers = raw.get("headers")
        if not isinstance(table, Tag) or not isinstance(headers, list):
            return None

        parsed: dict[str, Any] = {
            "table_type": table_classification,
            "headers": headers,
            "rows": TableParsingHelper.parse_table_with_pipeline(table, table_pipeline),
        }
        heading_path = raw.get("heading_path")
        if heading_path is not None:
            parsed["heading_path"] = heading_path
        return parsed


class DriverResultsSectionParser(TableSectionParser):
    def __init__(
        self,
        *,
        url: str,
        options: ScraperOptions,
        classifier: DriverResultsSectionTableClassifier | None = None,
        schema_factory: DriverResultsSchemaFactory | None = None,
        mapper: DriverResultsTableRecordMapper | None = None,
    ) -> None:
        super().__init__(
            section_id="driver_results",
            section_label="Driver results",
            include_heading_path=True,
            include_source_table=True,
            classifier=classifier,
            mapper=mapper,
        )
        self._url = url
        self._options = options
        self._schema_factory = schema_factory or DriverResultsSchemaFactory(
            unknown_value=UNKNOWN_VALUE,
        )

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

    def _build_pipeline(self, *, schema: TableSchemaDSL) -> TablePipeline:
        config = TableConfig(
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


__all__ = [
    "DriverResultsSectionParser",
    "DriverResultsSectionTableClassifier",
    "DriverResultsTableRecordMapper",
]
