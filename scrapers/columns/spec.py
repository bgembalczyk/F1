from dataclasses import dataclass

from scrapers.columns.base import BaseColumn
from scrapers.columns.ref import ColumnRef


@dataclass(frozen=True)
class ColumnSpec:
    header: str
    key: str
    column: BaseColumn | ColumnRef

    def build_column(self) -> BaseColumn:
        if isinstance(self.column, BaseColumn):
            return self.column
        return self.column.build()
