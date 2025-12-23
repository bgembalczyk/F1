import logging
from typing import Callable

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn

logger = logging.getLogger(__name__)


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
        log_errors: bool = False,
    ) -> None:
        super().__init__()
        self.predicate = predicate
        self.default = default
        self.log_errors = log_errors

    def parse(self, ctx: ColumnContext) -> bool:
        try:
            return bool(self.predicate(ctx))
        except (ValueError, TypeError, AttributeError, KeyError) as exc:
            if self.log_errors:
                logger.warning(
                    "BoolColumn predicate error for header=%s key=%s raw_text=%s exc_type=%s",
                    ctx.header,
                    ctx.key,
                    ctx.raw_text,
                    type(exc).__name__,
                )
            return self.default
