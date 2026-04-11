from typing import Any

from scrapers.columns.context import ColumnContext
from scrapers.helpers.background import extract_background


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
        bg = self._extract_raw_background(ctx)
        if bg is not None:
            record["background"] = bg

    @staticmethod
    def _extract_raw_background(ctx: ColumnContext) -> str | None:
        if ctx.cell is None:
            return None
        return extract_background(ctx.cell)


__all__ = ["BackgroundMixin"]
