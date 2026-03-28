"""Driver-specific parsing helpers.

This module contains helper functions for parsing driver-related data
from Wikipedia tables.
Extracted from scrapers/base/table/columns/helpers.py to follow SRP.

Follows SOLID principles:
- Single Responsibility: Handles only driver-related parsing
- High Cohesion: All functions work together for driver parsing
- Information Expert: Driver parsing logic grouped with driver data
"""

from bs4 import Tag

from models.records.link import LinkRecord
from scrapers.base.helpers.links import normalize_links
from scrapers.base.helpers.url import normalize_url
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.helpers.link_lookup import build_link_lookup


class DriverParsingHelpers:
    """
    Helper class for parsing driver information from table cells.

    Provides methods for:
    - Building driver link lookups
    - Parsing driver segments with metadata
    - Extracting driver information from complex cells
    """

    @staticmethod
    def build_link_lookup(
        links: list[LinkRecord],
    ) -> dict[str, list[LinkRecord]]:
        """
        Build lookup dictionary mapping driver names to their link records.

        Args:
            links: List of link records with 'text' and 'url' keys

        Returns:
            Dictionary mapping lowercase driver names to lists of matching links
        """
        return build_link_lookup(links)

    @staticmethod
    def parse_segment(
        segment: Tag,
        link_lookup: dict[str, list[LinkRecord]],
        base_url: str,
    ) -> LinkRecord | None:
        """
        Parse a driver segment (usually separated by <br>) into a LinkRecord.

        Args:
            segment: HTML tag containing driver information
            link_lookup: Pre-built lookup of driver names to links
            base_url: Base URL for resolving relative links

        Returns:
            LinkRecord with driver name and URL, or None if no valid driver found
        """
        links = normalize_links(
            segment,
            full_url=lambda href: normalize_url(base_url, href),
        )
        if not links:
            return None

        driver_link = links[0]
        driver_text = driver_link.get("text", "")
        if not driver_text:
            return None

        driver_key = driver_text.strip().lower()
        matched = link_lookup.get(driver_key, [driver_link])
        if matched:
            return matched[0]
        return driver_link

    @staticmethod
    def extract_from_context(
        ctx: ColumnContext,
        base_url: str,
    ) -> LinkRecord | None:
        """
        Extract driver information from column context.

        This is a higher-level function that combines link building and parsing.

        Args:
            ctx: Column context with cell and links
            base_url: Base URL for resolving relative links

        Returns:
            LinkRecord for the driver, or None if extraction fails
        """
        if not ctx.links:
            return None

        link_lookup = DriverParsingHelpers.build_link_lookup(ctx.links)

        if not ctx.cell:
            if ctx.links:
                return ctx.links[0]
            return None

        return DriverParsingHelpers.parse_segment(ctx.cell, link_lookup, base_url)

    @staticmethod
    def extract_rounds_text(text: str) -> str | None:
        """
        Extract rounds information from text (e.g., "Round 5-7" -> "Round 5-7").

        Args:
            text: Input text potentially containing round information

        Returns:
            Extracted rounds text, or None if not found
        """
        if not text:
            return None
        text = text.strip()
        if not text:
            return None
        if text.lower().startswith("round"):
            return text
        return None

    @staticmethod
    def strip_rounds_and_number(text: str) -> str:
        """
        Remove "Round X" or "#N" prefixes from driver text.

        Args:
            text: Input text with potential round/number prefixes

        Returns:
            Cleaned text without round/number information
        """
        text = text.strip()
        # Remove "Round X-Y"
        if text.lower().startswith("round"):
            parts = text.split(maxsplit=1)
            if len(parts) > 1:
                text = parts[1]
        # Remove leading "#N"
        if text.startswith("#"):
            parts = text.split(maxsplit=1)
            if len(parts) > 1:
                text = parts[1]
        return text.strip()
