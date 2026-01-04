import re
from typing import Any

from models.value_objects.normalized_date import NormalizedDate
from scrapers.base.helpers.time import parse_date_text
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.helpers import has_year
from scrapers.base.table.columns.types.base import BaseColumn


class DateRangeColumn(BaseColumn):
    """
    Parses date ranges from formats like "15–17 March" or "March 15–17".
    
    Returns dict: {"start": NormalizedDate, "end": NormalizedDate}
    """

    # Pattern for range separators
    _SEPARATOR_PATTERN = re.compile(r"\s*[–—-]\s*")

    def __init__(self, *, year: int | None = None) -> None:
        self.year = year

    def parse(self, ctx: ColumnContext) -> Any:
        text = (ctx.clean_text or "").strip()
        if not text:
            return None

        # Split text into start and end using separator
        parts = self._SEPARATOR_PATTERN.split(text, maxsplit=1)
        
        if len(parts) == 1:
            # Single date, not a range
            date = self._parse_single_date(text)
            if date:
                return {"start": date, "end": date}
            return None
        
        start_str, end_str = parts
        
        # Parse dates
        start_date = self._parse_single_date(start_str.strip())
        end_date = self._parse_single_date(end_str.strip())
        
        if start_date is None or end_date is None:
            return None
        
        return {
            "start": start_date,
            "end": end_date
        }

    def _parse_single_date(self, text: str) -> NormalizedDate | None:
        """
        Parses a single date.
        """
        if not text:
            return None
        
        # Add year if not present
        if self.year and not has_year(text):
            text = f"{text} {self.year}"
        
        parsed = parse_date_text(text)
        return NormalizedDate(text=parsed.raw, iso=parsed.iso)
