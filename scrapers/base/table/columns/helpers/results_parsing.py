"""Results and race data parsing helpers.

This module contains helper functions for parsing race results, points, and related data
from Wikipedia tables. Extracted from scrapers/base/table/columns/helpers.py to follow SRP.

Follows SOLID principles:
- Single Responsibility: Handles only results/race data parsing
- High Cohesion: All functions work together for results parsing
- Information Expert: Results parsing logic grouped with results data
"""

import re
from typing import Any

from bs4 import Tag

from scrapers.base.helpers.background import extract_background
from scrapers.base.helpers.parsing import parse_float_from_text
from scrapers.base.table.columns.constants import FRACTION_RE
from scrapers.base.table.columns.constants import SPLIT_RESULTS_RE
from scrapers.base.table.columns.context import ColumnContext


class ResultsParsingHelpers:
    """
    Helper class for parsing race results and points information.

    Provides methods for:
    - Parsing points values
    - Parsing race results with positions
    - Extracting entrant/team information
    - Parsing superscripts and metadata
    """

    @staticmethod
    def parse_points_value(text: str) -> float | None:
        """
        Parse points value from text, handling fractions.

        Supports formats like:
        - "25" -> 25.0
        - "12.5" -> 12.5
        - "1/2" -> 0.5
        - "1 1/2" -> 1.5
        - "57 1⁄7" -> 57.142857...

        Args:
            text: Text containing points value

        Returns:
            Parsed points as float, or None if invalid
        """
        if not text:
            return None

        text = text.strip()

        # Try fraction pattern first (e.g., "1/2", "1 1/2", "57 1⁄7")
        # Must be tried before simple float to avoid returning only the integer part
        match = FRACTION_RE.match(text)
        if match:
            whole = match.group("whole")
            numerator = match.group("numerator")
            denominator = match.group("denominator")

            value = 0.0
            if whole:
                value += float(whole)
            if numerator and denominator:
                value += float(numerator) / float(denominator)

            return value

        # Fall back to simple float (e.g., "25", "12.5")
        return parse_float_from_text(text)

    @staticmethod
    def parse_results(text: str) -> list[dict[str, Any]]:
        """
        Parse race results from text containing positions and status.

        Handles formats like:
        - "1st" -> [{"position": 1, "status": "finished"}]
        - "Ret" -> [{"status": "retired"}]
        - "DNS" -> [{"status": "did_not_start"}]
        - "1st/Ret" -> [{"position": 1}, {"status": "retired"}]

        Args:
            text: Text containing race result information

        Returns:
            List of result dictionaries
        """
        if not text:
            return []

        # Split on common separators
        parts = SPLIT_RESULTS_RE.split(text)
        results: list[dict[str, Any]] = []

        for part in parts:
            part = part.strip()
            if not part:
                continue

            result: dict[str, Any] = {}

            # Try to extract position
            pos_match = re.match(r"(\d+)(?:st|nd|rd|th)?", part, re.IGNORECASE)
            if pos_match:
                result["position"] = int(pos_match.group(1))
                result["status"] = "finished"
            else:
                # Common status codes
                part_upper = part.upper()
                if part_upper in {"RET", "RETIRED"}:
                    result["status"] = "retired"
                elif part_upper in {"DNS", "DID NOT START"}:
                    result["status"] = "did_not_start"
                elif part_upper in {"DNQ", "DID NOT QUALIFY"}:
                    result["status"] = "did_not_qualify"
                elif part_upper in {"DSQ", "DISQUALIFIED"}:
                    result["status"] = "disqualified"
                elif part_upper == "NC":
                    result["status"] = "not_classified"
                else:
                    result["status"] = part.lower()

            if result:
                results.append(result)

        return results

    @staticmethod
    def parse_superscripts(ctx: ColumnContext) -> tuple[int | None, bool, bool]:
        """
        Parse superscript markers from cell.

        Common superscripts in F1 tables:
        - Numbers: Indicate notes/references
        - † or *: Special markers for status

        Args:
            ctx: Column context with cell

        Returns:
            Tuple of (reference_number, has_dagger, has_asterisk)
        """
        if not ctx.cell:
            return None, False, False

        sups = ctx.cell.find_all("sup")

        reference_number = None
        has_dagger = False
        has_asterisk = False

        for sup in sups:
            text = sup.get_text(strip=True)

            # Try to parse as number
            if text.isdigit():
                reference_number = int(text)

            # Check for special markers
            if "†" in text or "‡" in text:
                has_dagger = True
            if "*" in text:
                has_asterisk = True

        return reference_number, has_dagger, has_asterisk

    @staticmethod
    def parse_entrant_segment(
        segment: Tag,
        link_lookup: dict[str, list[dict]],
        base_url: str,
    ) -> dict[str, Any]:
        """
        Parse entrant/team segment from table cell.

        Args:
            segment: HTML tag containing entrant information
            link_lookup: Pre-built lookup of entrant names to links
            base_url: Base URL for resolving relative links

        Returns:
            Dictionary with entrant data including name and title_sponsors list
        """
        from scrapers.base.helpers.links import normalize_links
        from scrapers.base.helpers.text import clean_wiki_text
        from scrapers.base.helpers.url import normalize_url

        links = normalize_links(
            segment,
            full_url=lambda href: normalize_url(base_url, href),
        )
        text = clean_wiki_text(segment.get_text(" ", strip=True))

        # Filter out empty-text links (e.g., flag image links)
        title_sponsors = [link for link in links if link.get("text")]

        return {
            "name": text,
            "title_sponsors": title_sponsors,
        }

    @staticmethod
    def extract_licenses(
        segments: list[Tag],
        base_url: str,
    ) -> list[dict[str, str]]:
        """
        Extract license information from segments.

        Args:
            segments: List of HTML tags containing license info
            base_url: Base URL for resolving relative links

        Returns:
            List of license records
        """
        from scrapers.base.helpers.links import normalize_links
        from scrapers.base.helpers.url import normalize_url

        licenses: list[dict[str, str]] = []
        for segment in segments:
            links = normalize_links(
                segment,
                full_url=lambda href: normalize_url(base_url, href),
            )
            if links:
                licenses.extend(links)

        return licenses

    @staticmethod
    def strip_refs(segment: Tag) -> None:
        """
        Remove reference markers from segment in-place.

        Args:
            segment: HTML tag to clean
        """
        for ref in segment.find_all("sup"):
            ref.decompose()

    @staticmethod
    def extract_number(text: str) -> int | None:
        """
        Extract first number from text.

        Args:
            text: Text potentially containing a number

        Returns:
            First number found, or None
        """
        if not text:
            return None

        match = re.search(r"\d+", text)
        if match:
            return int(match.group())

        return None

    @staticmethod
    def extract_race_result_background(cell: Tag) -> str | None:
        """
        Extract background color from race result cell.

        This is an alias for extract_background for semantic clarity.

        Args:
            cell: HTML table cell

        Returns:
            Background color string, or None
        """
        return extract_background(cell)

    @staticmethod
    def has_year(text: str) -> bool:
        """
        Check if text contains a 4-digit year (1900-2099).

        Args:
            text: Text to check

        Returns:
            True if contains a year pattern (1900-2099)
        """
        if not text:
            return False
        return bool(re.search(r"\b(19|20)\d{2}\b", text))
