from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from models.entity_name import EntityName
from models.section_id import SectionId
from scrapers.parser_table import HtmlTableParser
from scrapers.parsers.input_adapters import as_soup
from scrapers.pipeline_table import TablePipeline
from scrapers.section.serializer import build_section_parse_result

if TYPE_CHECKING:
    from scrapers.configs.public import TableConfig
    from scrapers.parsers.input_types import WikiParserInput
    from scrapers.section.parse_results import SectionParseResult

class TableSectionParser:
    """Generic section parser for single-table sections."""

    def __init__(
        self,
        *,
        config: TableConfig,
        section_id: SectionId | str,
        section_label: EntityName | str,
        domain: str,
        include_urls: bool,
        normalize_empty_values: bool,
    ) -> None:
        self._config = config
        self._section_id = SectionId.from_raw(section_id)
        self._section_label = EntityName.from_raw(section_label)
        self._domain = domain
        self._include_urls = include_urls
        self._normalize_empty_values = normalize_empty_values

    @property
    def section_id(self) -> SectionId:
        return self._section_id

    @property
    def section_label(self) -> EntityName:
        return self._section_label

    def parse(self, section_fragment: WikiParserInput) -> SectionParseResult:
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
            source="wikipedia",
            extras={"domain": self._domain},
        )
