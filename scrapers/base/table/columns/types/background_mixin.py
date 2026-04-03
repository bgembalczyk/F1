from typing import Any

from scrapers.base.helpers.background import extract_background
from scrapers.base.table.columns.context import ColumnContext


class BackgroundMixin:
    """
    Mixin dodający ekstrakcję koloru tła komórki do wyniku kolumny.

    Nadpisuje metodę apply() tak, aby po normalnym wykonaniu super().apply()
    dopisywał do rekordu klucz "background"
    z wartością koloru tła komórki (jeśli istnieje).

    Działa zarówno z BaseColumn (pojedyncze pola) jak i MultiColumn (wiele pól).
    """

    def apply(self, ctx: ColumnContext, record: dict[str, Any]) -> None:
        super().apply(ctx, record)  # type: ignore[misc]
        if ctx.cell is not None:
            bg = extract_background(ctx.cell)
            if bg is not None:
                record["background"] = bg
