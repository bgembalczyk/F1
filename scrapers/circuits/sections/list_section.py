from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.base.sections.table_section_parser import TableSectionParser

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.base.sections.interface import SectionParseResult
    from scrapers.base.table.config import TableScraperConfig


class CircuitsListSectionParser:
    def __init__(
        self,
        *,
        config: TableScraperConfig,
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

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        return self._parser.parse(section_fragment)
