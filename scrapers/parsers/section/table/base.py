from __future__ import annotations
from dataclasses import replace
from typing import TYPE_CHECKING
from typing import Any

from bs4 import BeautifulSoup

from models.entity_name import EntityName
from models.section_id import SectionId
from scrapers.parsers.table.html_table import HtmlTableParser
from scrapers.parsers.input_adapters import as_soup
from scrapers.parsers.wiki.section.base import BaseSectionParser
from scrapers.parsers.wiki.table.article import ArticleTablesParser
from scrapers.pipeline_table import TablePipeline
from scrapers.section.serializer import build_section_parse_result

if TYPE_CHECKING:
    from scrapers.configs.public import TableConfig
    from scrapers.section.parse_results import SectionParseResult


class TableSectionParser(BaseSectionParser):
    """Merged section parser supporting both single-table configured sections and template-method multiple HTML tables."""

    def __init__(
        self,
        *,
        section_id: SectionId | str = "unknown",
        section_label: EntityName | str = "Unknown",
        domain: str = "wikipedia",
        config: TableConfig | None = None,
        include_urls: bool = False,
        normalize_empty_values: bool = False,
        source: str = "wikipedia",
        metadata_extras: dict[str, Any] | None = None,
        include_heading_path: bool = False,
        include_source_table: bool = False,
    ) -> None:
        if config is not None:
            self._section_id = SectionId.from_raw(section_id)
            self._section_label = EntityName.from_raw(section_label)
        else:
            self._section_id = SectionId.from_raw(section_id)
            self._section_label = EntityName.from_raw(section_label)
        self._domain = domain
        self._config = config
        self._include_urls = include_urls
        self._normalize_empty_values = normalize_empty_values
        self._source = source
        self._metadata_extras = metadata_extras or {}
        if domain != "wikipedia":
            self._metadata_extras["domain"] = domain

        self._table_parser = ArticleTablesParser(
            include_heading_path=include_heading_path,
            include_source_table=include_source_table,
        )

    @property
    def section_id(self) -> SectionId:
        return self._section_id

    @property
    def section_label(self) -> EntityName:
        return self._section_label

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        if self._config is not None:
            return self._parse_with_config(section_fragment)
        return self.parse_fragment(section_fragment)

    def _parse_with_config(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        # di-antipattern-allow: section parser builds table parser per parse invocation.
        table_transport_parser = HtmlTableParser(
            section_id=None,
            expected_headers=self._config.expected_headers,
            table_css_class=self._config.table_css_class,
            section_domain=self._domain,
        )
        raw_config = replace(self._config, record_factory=None)
        pipeline = TablePipeline(
            config=raw_config,
            include_urls=self._include_urls,
            normalize_empty_values=self._normalize_empty_values,
        )
        records = pipeline.parse_rows(
            table_transport_parser.parse(as_soup(section_fragment)),
        )

        return build_section_parse_result(
            section_id=self._section_id,
            section_label=self._section_label,
            records=records,
            parser=self.__class__.__name__,
            source=self._source,
            extras=self._metadata_extras,
        )

    def parse_fragment(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        records: list[dict[str, Any]] = []
        for table_data in self._collect_tables(section_fragment):
            table_classification = self.classify_table(table_data)
            if table_classification is None:
                continue
            table_pipeline = self.build_pipeline(
                table_data=table_data,
                table_classification=table_classification,
            )
            mapped = self.parse_row(
                table_data=table_data,
                table_classification=table_classification,
                table_pipeline=table_pipeline,
            )
            if mapped is None:
                continue
            records.append(mapped)
        return self.build_result(records)

    def _collect_tables(
        self,
        section_fragment: BeautifulSoup,
    ) -> list[dict[str, Any]]:
        """Collect table payloads used by the section table template pipeline."""
        return self._parse_group(section_fragment)

    def _parse_group(
        self,
        section_fragment: BeautifulSoup,
    ) -> list[dict[str, Any]]:
        return self._table_parser.parse(section_fragment)

    def classify_table(self, table_data: dict[str, Any]) -> Any | None:
        return table_data

    def build_pipeline(
        self,
        *,
        table_data: dict[str, Any],
        table_classification: Any,
    ) -> Any:
        _ = table_data
        _ = table_classification
        return None

    def map_table_result(
        self,
        table_data: dict[str, Any],
        table_classification: Any,
        table_pipeline: Any,
    ) -> dict[str, Any] | None:
        """Transform a parsed table into a domain record (or skip with None)."""
        _ = table_data
        _ = table_pipeline
        raise NotImplementedError

    def parse_row(
        self,
        *,
        table_data: dict[str, Any],
        table_classification: Any,
        table_pipeline: Any,
    ) -> dict[str, Any] | None:
        return self.map_table_result(
            table_data=table_data,
            table_classification=table_classification,
            table_pipeline=table_pipeline,
        )

    def build_result(self, records: list[dict[str, Any]]) -> SectionParseResult:
        return build_section_parse_result(
            section_id=self._section_id,
            section_label=self._section_label,
            records=records,
            parser=self.__class__.__name__,
            source=self._source,
            extras=self._metadata_extras,
        )
