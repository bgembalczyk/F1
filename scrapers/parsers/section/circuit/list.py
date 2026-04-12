from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.configs.public import TableConfig
from scrapers.parsers.section.table.base import TableSectionParser
from scrapers.parsers.wiki.base_section_parser import BaseSectionParser
from scrapers.parsers.wiki.table.article import ArticleTablesParser
from scrapers.parsers.wiki.table.circuit_list_table_mapper import CircuitsListTableMapper
from scrapers.parsers.wiki.table.html import WikiTableHtmlParser
from scrapers.section.parse_results import SectionParseResult

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


class CircuitsListSectionParser(BaseSectionParser):
    def __init__(
        self,
        *,
        config: TableConfig,
        section_label: str | None = None,
        include_urls: bool,
        normalize_empty_values: bool,
        table_html_parser: WikiTableHtmlParser | None = None,
        table_domain_mapper: CircuitsListTableMapper | None = None,
    ) -> None:
        self._parser = TableSectionParser(
            config=config,
            section_id=config.section_id or "circuits",
            section_label=section_label or "Circuits",
            domain="circuits",
            include_urls=include_urls,
            normalize_empty_values=normalize_empty_values,
        )
        self._table_html_parser = table_html_parser or WikiTableHtmlParser()
        self._table_domain_mapper = table_domain_mapper or CircuitsListTableMapper()

    def _ensure_supported_table(self, section_fragment: BeautifulSoup) -> None:
        first_table = section_fragment.find("table", class_="wikitable")
        if first_table is not None:
            self._table_html_parser.parse(first_table)
        parsed_tables = ArticleTablesParser(
            specialized_mappers=[self._table_domain_mapper],
        ).parse(section_fragment)
        has_circuits_table = any(
            table.get("table_type") == "circuits_list" for table in parsed_tables
        )
        if not has_circuits_table:
            msg = "No circuits list table found in section section_fragment"
            raise RuntimeError(msg)

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        self._ensure_supported_table(section_fragment)
        return self._parser.parse(section_fragment)
