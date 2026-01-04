import re
from typing import Any

from models.value_objects.normalized_date import NormalizedDate
from scrapers.base.helpers.time import parse_date_text
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.helpers import has_year
from scrapers.base.table.columns.types.base import BaseColumn


class DateRangeColumn(BaseColumn):
    """
    Parsuje zakres dat z formatów typu "15–17 March" lub "March 15–17".
    
    Zwraca dict: {"start": NormalizedDate, "end": NormalizedDate}
    """

    # Pattern dla separatorów zakresu
    _SEPARATOR_PATTERN = re.compile(r"\s*[–—-]\s*")

    def __init__(self, *, year: int | None = None) -> None:
        self.year = year

    def parse(self, ctx: ColumnContext) -> Any:
        text = (ctx.clean_text or "").strip()
        if not text:
            return None

        # Dzielimy tekst na start i end używając separatora
        parts = self._SEPARATOR_PATTERN.split(text, maxsplit=1)
        
        if len(parts) == 1:
            # Pojedyncza data, nie zakres
            date = self._parse_single_date(text)
            if date:
                return {"start": date, "end": date}
            return None
        
        start_str, end_str = parts
        
        # Parsujemy daty
        start_date = self._parse_single_date(start_str.strip(), partial=True)
        end_date = self._parse_single_date(end_str.strip())
        
        if start_date is None or end_date is None:
            return None
        
        return {
            "start": start_date,
            "end": end_date
        }

    def _parse_single_date(self, text: str, partial: bool = False) -> NormalizedDate | None:
        """
        Parsuje pojedynczą datę.
        partial=True oznacza, że może to być niepełna data (np. tylko dzień bez miesiąca)
        """
        if not text:
            return None
        
        # Jeśli jest to tylko liczba i partial=True, traktujemy to jako dzień
        # który zostanie uzupełniony przez pełną datę końcową
        if partial and text.isdigit():
            # Zwracamy tymczasową strukturę, która będzie uzupełniona
            return NormalizedDate(text=text, iso=None)
        
        # Dodajemy rok jeśli go nie ma
        if self.year and not has_year(text):
            text = f"{text} {self.year}"
        
        parsed = parse_date_text(text)
        return NormalizedDate(text=parsed.raw, iso=parsed.iso)
