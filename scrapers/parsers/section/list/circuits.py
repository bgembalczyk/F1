from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.configs.public import TableConfig
from scrapers.parsers.roles import SectionParser
from scrapers.parsers.section.table.base import TableSectionParser
from scrapers.parsers.table.wiki.article import ArticleTablesParser
from scrapers.parsers.table.wiki.circuit_list import CircuitsListTableParser
from scrapers.section.parse_results import SectionParseResult

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


class CircuitsListSectionParser(SectionParser):
    def __init__(
        self,
        *,
        config: TableConfig,
        section_label: str | None = None,
        include_urls: bool,
        normalize_empty_values: bool,
    ) -> None:
        self._parser = TableSectionParser(
            config=config,
            section_id=config.section_id or "circuits",
            section_label=section_label or "Circuits",
            domain="circuits",
            include_urls=include_urls,
            normalize_empty_values=normalize_empty_values,
        )

    def _ensure_supported_table(self, fragment: BeautifulSoup) -> None:
        table_mapping_parser = CircuitsListTableParser()
        parsed_tables = ArticleTablesParser(
            specialized_parsers=[table_mapping_parser],
        ).parse(fragment)
        has_circuits_table = any(
            table.get("table_type") == "circuits_list" for table in parsed_tables
        )
        if not has_circuits_table:
            msg = "No circuits list table found in section fragment"
            raise RuntimeError(msg)

    def parse(self, fragment: BeautifulSoup) -> SectionParseResult:
        self._ensure_supported_table(fragment)
        return self._parser.parse(fragment)
