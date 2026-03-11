import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from bs4 import BeautifulSoup

from scrapers.base.helpers.multi_level_headers import MultiLevelHeaderBuilder
from scrapers.base.helpers.tables.header import is_repeated_header_row
from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.options import ScraperOptions
from scrapers.base.table.columns.types.driver import DriverColumn
from scrapers.base.table.columns.types.driver_list import DriverListColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.skip import SkipColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.dsl import column
from scrapers.base.table.parser import HtmlTableParser
from scrapers.base.table.scraper import F1TableScraper
from scrapers.base.transformers.failed_to_make_restart import (
    FailedToMakeRestartTransformer,
)
from scrapers.grands_prix.columns.restart_status import RestartStatusColumn

logger = logging.getLogger(__name__)


class RedFlaggedRacesBaseScraper(F1TableScraper):
    """
    Base scraper for red-flagged races tables.
    
    Provides common schema columns and fallback section ID logic
    for scraping red-flagged race data from Wikipedia.
    
    Subclasses should define their own CONFIG with specific:
    - url (typically the same for all red-flagged scrapers)
    - section_id (primary section to search for)
    - expected_headers (subset of headers to validate)
    - schema (can use build_common_red_flag_columns helper)
    - record_factory
    """

    # Subclasses can override to provide fallback section IDs
    alternative_section_ids: List[str] = []

    @staticmethod
    def build_common_red_flag_columns(race_name_header: str = "Grand Prix"):
        """
        Build common column definitions for red-flagged race tables.
        
        Args:
            race_name_header: Header name for the race (e.g., "Grand Prix" or "Event")
        
        Returns:
            List of column definitions common to all red-flagged race tables.
        """
        return [
            column("Year", "season", IntColumn()),
            column(race_name_header, race_name_header.lower().replace(" ", "_"), None),  # Will be set by caller
            column("Lap", "lap", IntColumn()),
            column("R", "restart_status", RestartStatusColumn()),
            column("Winner", "winner", DriverColumn()),
            column("Incident that prompted red flag", "incident", TextColumn()),
            column(
                "Failed to make the restart - Drivers",
                "failed_to_make_restart_drivers",
                DriverListColumn(),
            ),
            column(
                "Failed to make the restart - Reason",
                "failed_to_make_restart_reason",
                TextColumn(),
            ),
            column("Ref.", "ref", SkipColumn()),
        ]

    def __init__(
            self,
            *,
            options: ScraperOptions | None = None,
            config=None,
    ) -> None:
        options = options or ScraperOptions()
        options.transformers = list(options.transformers or []) + [
            FailedToMakeRestartTransformer(),
        ]
        super().__init__(options=options, config=config)

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        table, parser = self._find_table_with_fallbacks(soup)

        if table is None:
            self._log_toc_diagnostics(soup)
            error_msg = self._build_table_not_found_error(soup)
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        headers, header_rows = MultiLevelHeaderBuilder.build_headers(table)
        return self._parse_table_rows(table, parser, headers, header_rows)

    def _find_table_with_fallbacks(
            self, soup: BeautifulSoup,
    ) -> Tuple[Optional[Any], Optional[HtmlTableParser]]:
        """Try each candidate section ID in order and return the first matching table.

        Tries the primary section_id, then alternative_section_ids, then None
        (whole document). Returns a (table, parser) pair; both elements are None
        when no table is found.

        Args:
            soup: Parsed HTML document

        Returns:
            Tuple of (table Tag or None, HtmlTableParser or None).
        """
        section_ids_to_try = (
                                 [self.section_id] if self.section_id is not None else []
                             ) + self.alternative_section_ids + [None]

        for section_id in section_ids_to_try:
            logger.debug(f"Trying to find table with section_id={section_id!r}")
            current_parser = HtmlTableParser(
                section_id=section_id,
                expected_headers=self.expected_headers,
                table_css_class=self.table_css_class,
            )
            try:
                table = current_parser._find_table(soup)
                logger.info(f"Successfully found table with section_id={section_id!r}")
                return table, current_parser
            except RuntimeError as e:
                logger.debug(
                    f"Failed to find table with section_id={section_id!r}: {e}",
                )

        return None, None

    def _log_toc_diagnostics(self, soup: BeautifulSoup) -> None:
        """Emit a warning when the primary section exists in the TOC but has no heading.

        Args:
            soup: Parsed HTML document
        """
        if not self.section_id:
            return

        toc_ids = [
            f"toc-{self.section_id}",
            f"toc-{self.section_id.replace('_', '-')}",
            f"toc-{self.section_id.replace('-', '_')}",
        ]
        for toc_id in toc_ids:
            if soup.find(id=toc_id):
                logger.warning(
                    f"Found TOC entry '{toc_id}' but no matching section heading. "
                    f"Wikipedia page structure may be malformed or incomplete.",
                )

    def _build_table_not_found_error(self, soup: BeautifulSoup) -> str:
        """Build a descriptive error message when no matching table was found.

        Includes the section IDs that were tried, available page sections, and
        table counts so callers can diagnose Wikipedia page structure issues.

        Args:
            soup: Parsed HTML document

        Returns:
            Human-readable error string (also logged at ERROR level).
        """
        section_ids_to_try = (
                                 [self.section_id] if self.section_id is not None else []
                             ) + self.alternative_section_ids + [None]

        available_sections = [
            span.get('id', 'no-id')
            for span in soup.select('.mw-headline')
        ]
        sections_preview = available_sections[:10]
        if len(available_sections) > 10:
            sections_preview.append(f"... and {len(available_sections) - 10} more")

        all_tables = soup.find_all('table', class_=self.table_css_class)
        logger.error(
            f"Table search failed. Found {len(all_tables)} tables with "
            f"class='{self.table_css_class}' in the document.",
        )

        if all_tables:
            logger.error("Available tables and their headers:")
            for i, tbl in enumerate(all_tables[:5]):
                try:
                    headers, _ = MultiLevelHeaderBuilder.build_headers(tbl)
                    logger.error(f"  Table {i + 1}: {headers[:7]}...")
                except Exception as e:
                    logger.error(f"  Table {i + 1}: Could not extract headers - {e}")

        return (
            f"Nie znaleziono pasującej tabeli. "
            f"Próbowano sekcji: {section_ids_to_try}. "
            f"Dostępne sekcje na stronie: {sections_preview}. "
            f"Znaleziono {len(all_tables)} tabel z class='{self.table_css_class}'."
        )

    def _parse_table_rows(
            self,
            table,
            parser: HtmlTableParser,
            headers: List[str],
            header_rows: int,
    ) -> List[Dict[str, Any]]:
        """Parse data rows from the located table.

        Args:
            table: BeautifulSoup Tag for the <table> element
            parser: Configured HtmlTableParser used to locate the table
            headers: List of column header strings
            header_rows: Number of leading rows that are header rows (to skip)

        Returns:
            List of parsed record dicts.
        """
        records: list[dict[str, Any]] = []
        pending_rowspans: dict[int, dict[str, object]] = {}
        rows = table.find_all("tr")[header_rows:]
        for row_index, tr in enumerate(rows):
            cells = tr.find_all(["td", "th"])
            if not cells or all(not cell.get_text(strip=True) for cell in cells):
                continue

            cleaned_cells = [
                clean_wiki_text(cell.get_text(" ", strip=True)) for cell in cells
            ]
            if parser._is_footer_row(cells, cleaned_cells, headers):
                continue
            if is_repeated_header_row(cleaned_cells, headers):
                continue

            expanded_cells = parser._expand_row_cells(
                cells,
                headers,
                pending_rowspans,
            )
            record = self.extractor.pipeline.parse_cells(
                headers, expanded_cells, row_index=row_index,
            )
            if record:
                records.append(record)

        return records
