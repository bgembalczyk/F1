from typing import Callable

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.registry import column_type_registry
from scrapers.base.table.columns.types.base import BaseColumn


@column_type_registry.register("bool")
class BoolColumn(BaseColumn):
    """
    Kolumna zwracająca bool na podstawie predykatu.

    Predykat dostaje `ctx` (ColumnContext), czyli m.in.:
        - ctx.value     – wstępnie sparsowana wartość (jeśli jakaś poprzednia kolumna coś już zrobiła)
        - ctx.raw_text  – surowy tekst z komórki
        - ctx.cell      – Tag z BeautifulSoup
        - ctx.header    – nagłówek kolumny
        - ctx.key       – klucz po column_map

    Jeśli predykat rzuci wyjątek, zwracamy `default` (domyślnie False).
    """

    def __init__(
        self,
        predicate: Callable[[ColumnContext], bool],
        *,
        default: bool = False,
    ) -> None:
        super().__init__()
        self.predicate = predicate
        self.default = default

    def parse(self, ctx: ColumnContext) -> bool:
        try:
            return bool(self.predicate(ctx))
        except Exception:
            return self.default
