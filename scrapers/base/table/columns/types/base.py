from abc import ABC
from abc import abstractmethod

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.contracts import ColumnParseResult
from scrapers.base.table.columns.contracts import normalize_column_parse_result


class BaseColumn(ABC):
    """
    Bazowa klasa dla wszystkich typów kolumn.

    Domyślnie:
    - parse() zwraca wartość,
    - apply() zapisuje ją pod ctx.key w rekordzie,
      chyba że wartość == ctx.skip_sentinel.
    """

    @abstractmethod
    def parse(self, ctx: ColumnContext) -> ColumnParseResult | object:
        """
        Zwraca sparsowaną wartość dla danej komórki.
        """
        raise NotImplementedError

    def apply(self, ctx: ColumnContext, record: dict[str, object]) -> None:
        parsed = normalize_column_parse_result(
            self.parse(ctx),
            skip_sentinel=ctx.skip_sentinel,
        )
        if parsed.skip:
            return
        if ctx.model_fields is not None and ctx.key not in ctx.model_fields:
            return
        record[ctx.key] = parsed.value
