import re
from typing import Any

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


class TimeRangeColumn(BaseColumn):
    """
    Parsuje zakres godzin z formatów typu "9:00am–1:00pm" na format 24-godzinny.
    
    Zwraca dict: {"start": "09:00", "end": "13:00"} lub None jeśli parsowanie się nie powiedzie.
    """

    # Pattern dla czasu w formacie 12-godzinnym z am/pm
    _TIME_12H_PATTERN = re.compile(
        r"(\d{1,2}):(\d{2})\s*(am|pm)",
        re.IGNORECASE
    )
    
    # Pattern dla separatorów zakresu
    _SEPARATOR_PATTERN = re.compile(r"\s*[–—-]\s*")

    def parse(self, ctx: ColumnContext) -> Any:
        text = (ctx.clean_text or "").strip()
        if not text:
            return None

        # Dzielimy tekst na start i end używając separatora
        parts = self._SEPARATOR_PATTERN.split(text, maxsplit=1)
        if len(parts) != 2:
            return None

        start_str, end_str = parts
        
        # Parsujemy czas początkowy i końcowy
        start_time = self._parse_12h_time(start_str.strip())
        end_time = self._parse_12h_time(end_str.strip())
        
        if start_time is None or end_time is None:
            return None
        
        return {
            "start": start_time,
            "end": end_time
        }

    def _parse_12h_time(self, time_str: str) -> str | None:
        """
        Konwertuje czas z formatu 12-godzinnego na 24-godzinny.
        Np. "9:00am" -> "09:00", "1:00pm" -> "13:00"
        """
        match = self._TIME_12H_PATTERN.match(time_str)
        if not match:
            return None
        
        hours = int(match.group(1))
        minutes = match.group(2)
        period = match.group(3).lower()
        
        # Konwersja na format 24-godzinny
        if period == "am":
            if hours == 12:
                hours = 0
        else:  # pm
            if hours != 12:
                hours += 12
        
        return f"{hours:02d}:{minutes}"
