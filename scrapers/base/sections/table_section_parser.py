from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.base.table.config import ScraperConfig

from scrapers.base.sections.interface import SectionParseResult
from scrapers.base.sections.serializer import build_section_parse_result
from scrapers.base.table.parser import HtmlTableParser
from scrapers.base.table.pipeline import TablePipeline


class TableSectionParser:
    """Generic section parser for single-table sections."""

    def __init__(
        self,
        *,
        config: ScraperConfig,
        section_id: str,
        section_label: str,
        domain: str,
        include_urls: bool,
        normalize_empty_values: bool,
    ) -> None:
        self._config = config
        self._section_id = section_id
        self._section_label = section_label
        self._domain = domain
        self._include_urls = include_urls
        self._normalize_empty_values = normalize_empty_values

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        parser = HtmlTableParser(
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
        records = pipeline.parse_rows(parser.parse(section_fragment))

        return build_section_parse_result(
            section_id=self._section_id,
            section_label=self._section_label,
            records=records,
            parser=self.__class__.__name__,
            source="wikipedia",
            extras={"domain": self._domain},
        )
