"""Utility for extracting years and year ranges from text."""

import re
from typing import Any

from scrapers.base.helpers.constants import MIN_URLS_FOR_PATTERN
from scrapers.base.helpers.constants import SHORT_YEAR_LEN

YEAR_RANGE_RE = re.compile(r"\b(\d{4})\s*[-\u2013]\s*(\d{2,4})\b")
YEAR_RE = re.compile(r"\b(\d{4})\b")


class YearExtractor:
    """Handles extraction of years and year ranges from text."""

    @staticmethod
    def extract_years_from_text(text: str) -> set[int]:
        """Extract all years from text, expanding ranges.

        Handles cases like:
        - Individual years: 2002, 2005, 2007
        - Ranges: 2007-2008 or 2007-2008 (expands to all years in range)
        - Short ranges: 2018-19 (expands to 2018, 2019)

        Args:
            text: Text to extract years from

        Returns:
            Set of years found in the text
        """
        years_set: set[int] = set()

        # Find ranges like "2007-2008"
        for match in YEAR_RANGE_RE.finditer(text):
            start = int(match.group(1))
            end_text = match.group(2)
            if len(end_text) == SHORT_YEAR_LEN:
                # Handle short form like "2018-19"
                end = (start // 100) * 100 + int(end_text)
            else:
                end = int(end_text)
            for year in range(start, end + 1):
                years_set.add(year)

        # Find individual years
        for match in YEAR_RE.finditer(text):
            year = int(match.group(1))
            years_set.add(year)

        return years_set

    @staticmethod
    def build_year_to_url_map(
        links: list[dict[str, Any]],
        url_key: str = "url",
        text_key: str = "text",
    ) -> dict[int, str | None]:
        """Build a mapping from year to URL from a list of links.

        Args:
            links: List of link dictionaries
            url_key: Key for URL in link dictionary
            text_key: Key for text in link dictionary

        Returns:
            Dictionary mapping year to URL
        """
        year_to_url: dict[int, str | None] = {}
        for link in links:
            link_text = link.get(text_key, "")
            year_match = YEAR_RE.search(link_text)
            if year_match:
                year = int(year_match.group(1))
                year_to_url[year] = link.get(url_key)
        return year_to_url

    @staticmethod
    def detect_url_pattern(year_to_url: dict[int, str | None]) -> str | None:
        """Detect a predictable URL pattern from available year links.

        Returns a pattern string with {year} placeholder if pattern is predictable.

        Args:
            year_to_url: Dictionary mapping year to URL

        Returns:
            Pattern string with {year} placeholder, or None if no pattern found
        """
        urls = [(year, url) for year, url in year_to_url.items() if url]
        if len(urls) < MIN_URLS_FOR_PATTERN:
            return None

        # Check if all URLs follow the same pattern
        patterns = []
        for year, url in urls:
            # Replace the year in URL with a placeholder
            pattern = url.replace(str(year), "{year}")
            patterns.append(pattern)

        # If all patterns are the same, we found a predictable pattern
        if len(set(patterns)) == 1:
            return patterns[0]

        return None

    @staticmethod
    def interpolate_urls(
        years_set: set[int],
        year_to_url: dict[int, str | None],
    ) -> dict[int, str | None]:
        """Interpolate missing URLs using detected pattern.

        Args:
            years_set: Set of years to interpolate URLs for
            year_to_url: Existing year to URL mapping

        Returns:
            Updated year to URL mapping with interpolated URLs
        """
        result = dict(year_to_url)

        if len(year_to_url) >= MIN_URLS_FOR_PATTERN:
            url_pattern = YearExtractor.detect_url_pattern(year_to_url)
            if url_pattern:
                for year in years_set:
                    if year not in result:
                        result[year] = url_pattern.replace("{year}", str(year))

        return result
