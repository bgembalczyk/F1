from typing import Any

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn
from scrapers.base.table.constants import SEPARATOR_PATTERN
from scrapers.base.table.constants import TIME_12H_PATTERN


class TimeRangeColumn(BaseColumn):
    """
    Parses time ranges from formats like "9:00am-1:00pm" to 24-hour format.

    Returns dict: {"start": "09:00", "end": "13:00"} or None if parsing fails.
    """

    def parse(self, ctx: ColumnContext) -> Any:
        text = (ctx.clean_text or "").strip()
        if not text:
            return None

        # Split text into start and end using separator
        parts = SEPARATOR_PATTERN.split(text, maxsplit=1)
        expected_parts = 2
        if len(parts) != expected_parts:
            return None

        start_str, end_str = parts

        # Parse start and end times
        start_time = self._parse_12h_time(start_str.strip())
        end_time = self._parse_12h_time(end_str.strip())

        if start_time is None or end_time is None:
            return None

        return {"start": start_time, "end": end_time}

    def _parse_12h_time(self, time_str: str) -> str | None:
        """
        Converts time from 12-hour format to 24-hour format.
        E.g., "9:00am" -> "09:00", "1:00pm" -> "13:00"
        """
        match = TIME_12H_PATTERN.match(time_str)
        if not match:
            return None

        hours = int(match.group(1))
        minutes = match.group(2)
        period = match.group(3).lower()

        # Convert to 24-hour format
        if period == "am":
            noon_hour = 12
            if hours == noon_hour:
                hours = 0
        else:
            noon_hour = 12
            if hours != noon_hour:
                hours += noon_hour

        return f"{hours:02d}:{minutes}"
