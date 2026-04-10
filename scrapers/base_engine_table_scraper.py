"""Base scraper for engine-related table scrapers with custom parsing logic."""

from abc import ABC
from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.table.parser import HtmlTableParser
from scrapers.base.table.scraper import F1TableScraper


class BaseEngineTableScraper(F1TableScraper, ABC):
    """Domain-focused base for engine tables."""

    def build_parser(self) -> HtmlTableParser:
        return HtmlTableParser(
            section_id=self.section_id,
            expected_headers=self.expected_headers,
            table_css_class=self.table_css_class,
        )

    def _find_table(self, soup: BeautifulSoup) -> Tag:
        return self.build_parser().find_table(soup)

    def _is_valid_row(
        self,
        cells: list[Tag],
        cleaned_cells: list[str],
        headers: list[str],
    ) -> bool:
        if not cells or all(not cell.get_text(strip=True) for cell in cells):
            return False
        return not self.build_parser().is_footer_row(cells, cleaned_cells, headers)

    def _clean_cells(self, cells: list[Tag]) -> list[str]:
        return [clean_wiki_text(cell.get_text(" ", strip=True)) for cell in cells]

    def build_record(
        self,
        headers: list[str],
        cells: list[Tag],
        row_index: int,
    ) -> dict[str, Any] | None:
        return self.extractor.pipeline.parse_cells(
            headers,
            cells,
            row_index=row_index,
        )

    def _parse_record(
        self,
        headers: list[str],
        cells: list[Tag],
        row_index: int,
    ) -> dict[str, Any] | None:
        return self.build_record(headers, cells, row_index)
