from __future__ import annotations

from collections.abc import Callable

from scrapers.base.export.export_helpers import fieldnames_from_first_row
from scrapers.base.export.export_helpers import fieldnames_from_union
from validation.validator_base import ExportRecord


class FieldnamesStrategySelector:
    def __init__(
        self,
        *,
        strategies: dict[str, Callable[[list[ExportRecord]], list[str]]] | None = None,
    ) -> None:
        self._strategies = strategies or {
            "union": fieldnames_from_union,
            "first_row": fieldnames_from_first_row,
        }

    def resolve(self, data: list[ExportRecord], *, strategy: str) -> list[str]:
        resolver = self._strategies.get(strategy)
        if resolver is None:
            msg = (
                "Nieznana strategia fieldnames: "
                f"{strategy!r}. Dostępne: "
                f"{', '.join(repr(s) for s in self._strategies)}."
            )
            raise ValueError(msg)
        return resolver(data)
