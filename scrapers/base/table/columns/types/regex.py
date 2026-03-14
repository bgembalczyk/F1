import re
from collections.abc import Callable
from typing import Any

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


class RegexColumn(BaseColumn):
    """
    Kolumna wyciągająca fragment tekstu na podstawie regexa
    i opcjonalnie rzutująca go na typ.

    pattern        – regex z grupą przechwytującą (domyślnie group=1)
    group          – numer grupy przechwytującej
    cast           – funkcja typu str -> Any (np. float, int)
    default        – wartość gdy brak dopasowania lub błąd rzutowania
    normalize_number – jeśli True, usuwa ',' z liczby przed castem
    flags          – flagi regexa (domyślnie IGNORECASE)
    """

    def __init__(
        self,
        pattern: str,
        *,
        group: int = 1,
        cast: Callable[[str], Any] | None = None,
        default: Any = None,
        normalize_number: bool = False,
        flags: int = re.IGNORECASE,
    ) -> None:
        self._re = re.compile(pattern, flags=flags)
        self.group = group
        self.cast = cast
        self.default = default
        self.normalize_number = normalize_number

    def parse(self, ctx: ColumnContext) -> Any:
        text = (ctx.clean_text or "").replace("\xa0", " ")
        m = self._re.search(text)
        if not m:
            return self.default

        s = m.group(self.group).strip()
        if self.normalize_number:
            s = s.replace(",", "")

        if self.cast is None:
            return s

        try:
            return self.cast(s)
        except (ValueError, TypeError):
            return self.default
