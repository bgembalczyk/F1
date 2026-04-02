from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.base.sections.interface import SectionParser
from scrapers.base.sections.table_section_parser import TableSectionParser
from scrapers.circuits.sections.list_table import CircuitsListTableParser
from scrapers.wiki.parsers.elements.article_tables import ArticleTablesParser

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.base.sections.interface import SectionParseResult
    from scrapers.base.table.config import ScraperConfig


class CircuitsListSectionParser(SectionParser):
    def __init__(
        self,
        *,
        config: ScraperConfig,
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

    def _ensure_supported_table(self, section_fragment: BeautifulSoup) -> None:
        parsed_tables = ArticleTablesParser(
            specialized_parsers=[CircuitsListTableParser()],
        ).parse(section_fragment)
        has_circuits_table = any(
            table.get("table_type") == "circuits_list" for table in parsed_tables
        )
        if not has_circuits_table:
            msg = "No circuits list table found in section fragment"
            raise RuntimeError(msg)

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        self._ensure_supported_table(section_fragment)
        return self._parser.parse(section_fragment)
