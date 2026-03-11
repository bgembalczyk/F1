from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Dict

from scrapers.base.table.columns.context import ColumnContext


class BaseColumn(ABC):
    """
    Bazowa klasa dla wszystkich typów kolumn.

    Domyślnie:
    - parse() zwraca wartość,
    - apply() zapisuje ją pod ctx.key w rekordzie,
      chyba że wartość == ctx.skip_sentinel.
    """

    @abstractmethod
    def parse(self, ctx: ColumnContext) -> Any:
        """
        Zwraca sparsowaną wartość dla danej komórki.
        """
        raise NotImplementedError

    def apply(self, ctx: ColumnContext, record: Dict[str, Any]) -> None:
        value = self.parse(ctx)
        if value is ctx.skip_sentinel:
            return
        if ctx.model_fields is not None and ctx.key not in ctx.model_fields:
            return
        record[ctx.key] = value
