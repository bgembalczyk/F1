"""Base scraper for engine-related table scrapers with custom parsing logic."""

from abc import ABC
from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.table.parser import HtmlTableParser
from scrapers.base.table.scraper import F1TableScraper


class BaseEngineTableScraper(F1TableScraper, ABC):
    """
    Base class for engine scrapers that require custom table parsing.

    Provides common infrastructure for:
    - Custom header extraction
    - Row validation and filtering
    - Cell expansion for rowspans

    Follows SOLID principles:
    - Single Responsibility: Handles only engine table parsing concerns
    - Open/Closed: Extensible through hooks without modification
    - DRY: Eliminates duplicate parsing code across engine scrapers
    """

    def _create_parser(self) -> HtmlTableParser:
        """Create HTML table parser with scraper configuration."""
        return HtmlTableParser(
            section_id=self.section_id,
            expected_headers=self.expected_headers,
            table_css_class=self.table_css_class,
        )

    def _find_table(self, soup: BeautifulSoup) -> Tag:
        """Find the target table in the HTML document."""
        parser = self._create_parser()
        return parser.find_table(soup)

    def _is_valid_row(
        self,
        cells: list[Tag],
        cleaned_cells: list[str],
        headers: list[str],
    ) -> bool:
        """
        Validate if a row should be processed.

        Override this method to add custom validation logic.
        """
        # Empty rows
        if not cells or all(not cell.get_text(strip=True) for cell in cells):
            return False

        # Footer rows
        parser = self._create_parser()
        return not parser.is_footer_row(cells, cleaned_cells, headers)

    def _clean_cells(self, cells: list[Tag]) -> list[str]:
        """Clean cell text content."""
        return [clean_wiki_text(cell.get_text(" ", strip=True)) for cell in cells]

    def _parse_record(
        self,
        headers: list[str],
        cells: list[Tag],
        row_index: int,
    ) -> dict[str, Any] | None:
        """Parse a single row into a record using the extractor pipeline."""
        return self.extractor.pipeline.parse_cells(
            headers,
            cells,
            row_index=row_index,
        )
