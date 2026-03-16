from __future__ import annotations

from bs4 import BeautifulSoup

from scrapers.base.sections.interface import SectionParseResult
from scrapers.base.sections.table_section_parser import TableSectionParser
from scrapers.base.table.config import ScraperConfig


class ConstructorsListSectionParser:
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
            section_id=config.section_id or "constructors",
            section_label=section_label or "Constructors",
            domain="constructors",
            include_urls=include_urls,
            normalize_empty_values=normalize_empty_values,
        )

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        return self._parser.parse(section_fragment)
