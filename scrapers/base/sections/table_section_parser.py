from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING
from typing import Any

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.base.table.config import ScraperConfig

from scrapers.base.sections.interface import SectionParseResult
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
        records: list[dict[str, Any]] = []
        for row_index, row in enumerate(parser.parse(section_fragment)):
            parsed = pipeline.parse_cells(
                row.headers,
                row.cells,
                row_index=row_index,
                header_cells=row.header_cells,
            )
            if parsed:
                records.append(parsed)

        return SectionParseResult(
            section_id=self._section_id,
            section_label=self._section_label,
            records=records,
            metadata={"parser": self.__class__.__name__, "domain": self._domain},
        )
