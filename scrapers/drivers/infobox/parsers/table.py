"""Helper class for parsing nested tables from infobox cells."""

import contextlib
import re
from typing import Any

from bs4 import Tag

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
        """Check if table is a Wins/Podiums/Poles or Wins/Top tens/Poles stats table.

        Args:
            table_data: Dictionary with parsed table data

        Returns:
            True if this is a recognized stats table format
        """
        headers = table_data.get("headers", [])
        if len(headers) != EXPECTED_STATS_COLUMNS:
            return False
        # Normalize headers for comparison
        normalized = [h.lower().strip() for h in headers]
        expected_wins_podiums_poles = ["wins", "podiums", "poles"]
        expected_wins_topten_poles = ["wins", "top tens", "poles"]
        return normalized in (expected_wins_podiums_poles, expected_wins_topten_poles)

    @staticmethod
    def _extract_stats_from_table(table_data: dict[str, Any]) -> dict[str, int | None]:
        """Extract Wins, Podiums/Top tens, Poles from stats table.

        Args:
            table_data: Dictionary with parsed table data

        Returns:
            Dictionary with wins, podiums, top_tens, and poles statistics
        """
        headers = table_data.get("headers", [])
        normalized = [h.lower().strip() for h in headers]

        stats: dict[str, int | None] = {
            "wins": None,
            "podiums": None,
            "top_tens": None,
            "poles": None,
        }
        rows = table_data.get("rows", [])
        if rows and len(rows[0]) >= EXPECTED_STATS_COLUMNS:
            # First row contains the values
            # Determine if we have podiums or top tens based on header
            has_podiums = "podiums" in normalized
            has_top_tens = "top tens" in normalized

            with contextlib.suppress(ValueError, IndexError):
                stats["wins"] = int(rows[0][0])

            # Second column is either podiums or top tens
            if has_podiums:
                with contextlib.suppress(ValueError, IndexError):
                    stats["podiums"] = int(rows[0][1])
            elif has_top_tens:
                with contextlib.suppress(ValueError, IndexError):
                    stats["top_tens"] = int(rows[0][1])

            with contextlib.suppress(ValueError, IndexError):
                stats["poles"] = int(rows[0][2])

        # Remove None values for cleaner output
        return {k: v for k, v in stats.items() if v is not None}
