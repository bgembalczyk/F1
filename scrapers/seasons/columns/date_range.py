import re
from typing import Any

from models.value_objects.normalized_date import NormalizedDate
from scrapers.base.helpers.time import parse_date_text
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.helpers.results_parsing import ResultsParsingHelpers
from scrapers.base.table.columns.types.base import BaseColumn
from scrapers.seasons.columns.helpers.constants import SEPARATOR_PATTERN


class DateRangeColumn(BaseColumn):
    """
    Parses date ranges from formats like "15-17 March" or "March 15-17".

    Returns dict: {"start": NormalizedDate, "end": NormalizedDate}
    """
    def __init__(self, *, year: int | None = None) -> None:
        self.year = year

    def parse(self, ctx: ColumnContext) -> Any:
        text = (ctx.clean_text or "").strip()
        if not text:
            return None

        # Split text into start and end using separator
        parts = SEPARATOR_PATTERN.split(text, maxsplit=1)

        if len(parts) == 1:
            # Single date, not a range
            date = self._parse_single_date(text)
            if date:
                return {"start": date, "end": date}
            return None

        start_str, end_str = parts
        start_str = start_str.strip()
        end_str = end_str.strip()

        # If start is just a day number, infer month/year from end
        if start_str.isdigit():
            # Extract month and year from end_str
            # Add year if not present in end_str
            full_end = end_str
            if self.year and not ResultsParsingHelpers.has_year(full_end):
                full_end = f"{full_end} {self.year}"

            # Try to extract month name from end_str for start
            month_match = re.search(
                (
                    r"\b("
                    r"January|February|March|April|May|June|July|August|"
                    r"September|October|November|December|Jan|Feb|Mar|Apr|"
                    r"May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec"
                    r")\b"
                ),
                end_str,
                re.IGNORECASE,
            )
            if month_match:
                month_name = month_match.group(1)
                start_str = f"{start_str} {month_name}"
                if self.year and not ResultsParsingHelpers.has_year(start_str):
                    start_str = f"{start_str} {self.year}"

        # Parse dates
        start_date = self._parse_single_date(start_str)
        end_date = self._parse_single_date(end_str)

        if start_date is None or end_date is None:
            return None

        return {"start": start_date, "end": end_date}

    def _parse_single_date(self, text: str) -> NormalizedDate | None:
        """
        Parses a single date.
        """
        if not text:
            return None

        # Add year if not present
        if self.year and not ResultsParsingHelpers.has_year(text):
            text = f"{text} {self.year}"

        parsed = parse_date_text(text)
        return NormalizedDate(text=parsed.raw, iso=parsed.iso)
