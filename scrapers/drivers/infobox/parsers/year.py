"""Helper class for parsing year-related information from infobox cells."""

import re

from models.domain_utils.years import parse_year_range as parse_domain_year_range
from scrapers.base.error_handler import ErrorHandler
from scrapers.base.helpers.text_normalization import clean_infobox_text
from scrapers.drivers.infobox.parsers.constants import MIN_RANGE_YEARS

_YEAR_RE = re.compile(r"\b(\d{4})\b")
_OPEN_ENDED_RE = re.compile(r"\b(\d{4})\s*[-\u2013]\s*(?:present)?$")


class YearParser:
    """Handles parsing of years and year ranges."""

    @staticmethod
    def parse_year_range(text: str) -> dict[str, int | None]:
        """Parse year range from text."""
        normalized = clean_infobox_text(text) or ""
        return ErrorHandler.run_domain_parse(
            lambda: parse_domain_year_range(normalized),
            message=f"Nie udało się sparsować zakresu lat: {text!r}.",
            parser_name=YearParser.__name__,
        )

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

        # Extract all years upfront
        all_years = _YEAR_RE.findall(year_text)

        # Handle "until YEAR"
        if "until" in year_text.lower():
            if all_years:
                years["end"] = int(all_years[0])
        # Handle open-ended values like "YEAR-" (optionally with "present")
        elif _OPEN_ENDED_RE.search(year_text.strip()):
            if all_years:
                years["start"] = int(all_years[0])
        # Handle "YEAR-YEAR" or "YEAR-YEAR"
        elif len(all_years) >= MIN_RANGE_YEARS:
            years["start"] = int(all_years[0])
            years["end"] = int(all_years[-1])
        elif len(all_years) == 1:
            # Single year without context (e.g., just "(2015)")
            # Treat as a single-year validity period.
            # Reasonable assumption for one-year licences.
            years["start"] = int(all_years[0])
            years["end"] = int(all_years[0])

        return years
