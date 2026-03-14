"""Helper class for parsing year-related information from infobox cells."""

import re

from scrapers.base.errors import DomainParseError
from scrapers.base.helpers.text_normalization import clean_infobox_text
from scrapers.base.helpers.year_extraction import YearExtractor


class YearParser:
    """Handles parsing of years and year ranges."""

    @staticmethod
    def parse_year_range(text: str) -> dict[str, int | None]:
        """Parse year range from text.

        Handles cases like:
        - "2018-2022" -> {start: 2018, end: 2022}
        - "2018-19–2022" -> {start: 2018, end: 2022}  # Multiple dashes
        - "2018" -> {start: 2018, end: 2018}
        - "2015–present" -> {start: 2015, end: None}
        """
        try:
            normalized = clean_infobox_text(text) or ""

            # Check for "present" keyword
            has_present = (
                re.search(r"\bpresent\b", normalized, re.IGNORECASE) is not None
            )

            # Extract all 4-digit years and 2-digit years
            all_years = []

            # Find all standalone 4-digit years
            four_digit_years = [int(y) for y in re.findall(r"\b(\d{4})\b", normalized)]
            all_years.extend(four_digit_years)

            # Find 2-digit years that come after 4-digit years (like "2018-19")
            two_digit_pattern = re.finditer(r"\b(\d{4})\s*[-–]\s*(\d{2})\b", normalized)
            for match in two_digit_pattern:
                start_year = int(match.group(1))
                end_suffix = match.group(2)
                end_year = (start_year // 100) * 100 + int(end_suffix)
                if end_year not in all_years:
                    all_years.append(end_year)

            if not all_years:
                return {"start": None, "end": None}

            # Sort years and take first and last
            all_years.sort()
            start = all_years[0]
            # If "present" is in text, end should be None
            end = None if has_present else all_years[-1]

            return {"start": start, "end": end}
        except (TypeError, ValueError) as exc:
            raise DomainParseError(
                f"Nie udało się sparsować zakresu lat: {text!r}.",
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
        - "(2020–)" -> {start: 2020, end: None}
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
        # Handle "YEAR–" or "YEAR-" (open-ended, possibly with "present")
        elif re.search(r"\b(\d{4})\s*[–-]\s*(?:present)?$", year_text.strip()):
            year_match = re.search(r"\b(\d{4})\b", year_text)
            if year_match:
                years["start"] = int(year_match.group(1))
        # Handle "YEAR–YEAR" or "YEAR-YEAR"
        else:
            all_years = re.findall(r"\b(\d{4})\b", year_text)
            if len(all_years) >= 2:
                years["start"] = int(all_years[0])
                years["end"] = int(all_years[-1])
            elif len(all_years) == 1:
                # Single year without context (e.g., just "(2015)")
                # Treat as a single-year validity period (both start and end are the same)
                # This is a reasonable assumption for racing licences that were valid only in one year
                years["start"] = int(all_years[0])
                years["end"] = int(all_years[0])

        return years
