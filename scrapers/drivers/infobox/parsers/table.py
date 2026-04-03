"""Helper class for parsing nested tables from infobox cells."""

import re
from typing import Any

from bs4 import Tag

from models.domain_utils.field_normalization.stats import extract_driver_stats_row
from models.domain_utils.field_normalization.stats import is_driver_stats_table
from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.helpers.text_normalization import clean_infobox_text
from scrapers.drivers.infobox.parsers.constants import EXPECTED_STATS_COLUMNS
from scrapers.drivers.infobox.parsers.link_extractor import InfoboxLinkExtractor


class TableParser:
    """Handles parsing of nested tables and extraction of statistics."""

    def __init__(self, link_extractor: InfoboxLinkExtractor):
        """Initialize the table parser.

        Args:
            link_extractor: Link extractor for extracting URLs from cells
        """
        self._link_extractor = link_extractor

    def parse_full_data(
        self,
        cell: Tag,
        *,
        include_urls: bool,
    ) -> dict[str, Any]:
        """Parse full data including nested tables and structured information.

        Args:
            cell: BeautifulSoup Tag representing the cell
            include_urls: Whether to include URL information

        Returns:
            Dictionary with parsed data (text, links, and optional table info)
        """
        text = clean_infobox_text(cell.get_text(" ", strip=True))

        nested_table = cell.find("table")
        if nested_table:
            table_data = self.parse_nested_table(nested_table)
            # Check if this is a Wins/Podiums/Poles table or Wins/Top tens/Poles table
            if self._is_stats_table(table_data):
                # Extract the values directly and return only stats
                return self._extract_stats_from_table(table_data)
            # For other tables, include full metadata
            payload: dict[str, Any] = {"text": text}
            if include_urls:
                payload["links"] = self._link_extractor.extract_links(cell)
            payload["table"] = table_data
            return payload

        # Check if this is "X races run over Y years" pattern
        # Only run regex if text is not None
        if text is not None:
            races_run_match = re.match(r"^(\d+)\s+races?\s+run\s+over", text)
            if races_run_match:
                return {"races_run": int(races_run_match.group(1))}

        # Default: return text and links
        payload: dict[str, Any] = {"text": text}
        if include_urls:
            payload["links"] = self._link_extractor.extract_links(cell)
        return payload

    @staticmethod
    def parse_nested_table(table: Tag) -> dict[str, Any]:
        """Parse a nested HTML table into structured data.

        Args:
            table: BeautifulSoup Tag representing the table

        Returns:
            Dictionary with 'headers' and 'rows' keys
        """
        rows = table.find_all("tr")
        if not rows:
            return {"headers": [], "rows": []}
        header_cells = rows[0].find_all(["th", "td"])
        headers = [clean_wiki_text(c.get_text(" ", strip=True)) for c in header_cells]
        data_rows: list[list[str]] = []
        for row in rows[1:]:
            cells = [
                clean_wiki_text(c.get_text(" ", strip=True))
                for c in row.find_all(["th", "td"])
            ]
            if cells:
                data_rows.append(cells)
        return {"headers": headers, "rows": data_rows}

    @staticmethod
    def _is_stats_table(table_data: dict[str, Any]) -> bool:
        """Check if table is a Wins/Podiums/Poles or Wins/Top tens/Poles stats table."""
        headers = table_data.get("headers", [])
        return is_driver_stats_table(headers, expected_columns=EXPECTED_STATS_COLUMNS)

    @staticmethod
    def _extract_stats_from_table(table_data: dict[str, Any]) -> dict[str, int | None]:
        """Extract Wins, Podiums/Top tens, Poles from stats table."""
        headers = table_data.get("headers", [])
        rows = table_data.get("rows", [])
        if not rows or len(rows[0]) < EXPECTED_STATS_COLUMNS:
            return {}
        return extract_driver_stats_row(rows[0], headers)
