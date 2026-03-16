"""Helper class for parsing year-related information from infobox cells."""

import re

from models.domain_utils.years import parse_year_range as parse_domain_year_range
from scrapers.base.errors import DomainParseError
from scrapers.base.helpers.text_normalization import clean_infobox_text
from scrapers.base.helpers.year_extraction import YearExtractor


class YearParser:
    MIN_RANGE_YEARS = 2

    """Handles parsing of years and year ranges."""

    @staticmethod
    def parse_year_range(text: str) -> dict[str, int | None]:
        """Parse year range from text."""
        try:
            normalized = clean_infobox_text(text) or ""
            return parse_domain_year_range(normalized)
        except (TypeError, ValueError) as exc:
            msg = f"Nie udało się sparsować zakresu lat: {text!r}."
            raise DomainParseError(
                msg,
                cause=exc,
            ) from exc

    @staticmethod
    def detect_url_pattern(year_to_link: dict[int, str | None]) -> str | None:
        """Detect a predictable URL pattern from available year links.

        Returns a pattern string with {year} placeholder if pattern is predictable.
        """
        return YearExtractor.detect_url_pattern(year_to_link)

    @staticmethod
    def parse_licence_years(year_text: str) -> dict[str, int | None]:
        """Parse year information from licence year text.

        Handles formats like:
        - "(until 2019)" -> {start: None, end: 2019}
        - "(2020-)" -> {start: 2020, end: None}
        - "(2015-2018)" -> {start: 2015, end: 2018}
        """
        years: dict[str, int | None] = {"start": None, "end": None}

        # Remove parentheses if present
        year_text = year_text.strip("()")

        # Handle "until YEAR"
        if "until" in year_text.lower():
            year_match = re.search(r"\b(\d{4})\b", year_text)
            if year_match:
                years["end"] = int(year_match.group(1))
        # Handle open-ended values like "YEAR-" (optionally with "present")
        elif re.search(r"\b(\d{4})\s*[-\u2013]\s*(?:present)?$", year_text.strip()):
            year_match = re.search(r"\b(\d{4})\b", year_text)
            if year_match:
                years["start"] = int(year_match.group(1))
        # Handle "YEAR-YEAR" or "YEAR-YEAR"
        else:
            all_years = re.findall(r"\b(\d{4})\b", year_text)
            if len(all_years) >= YearParser.MIN_RANGE_YEARS:
                years["start"] = int(all_years[0])
                years["end"] = int(all_years[-1])
            elif len(all_years) == 1:
                # Single year without context (e.g., just "(2015)")
                # Treat as a single-year validity period.
                # Reasonable assumption for one-year licences.
                years["start"] = int(all_years[0])
                years["end"] = int(all_years[0])

        return years
