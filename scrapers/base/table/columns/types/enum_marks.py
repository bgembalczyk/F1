from typing import Any
from typing import Dict

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


class EnumMarksColumn(BaseColumn):
    """
    Ogólny enum_column dla znaków (np. *, †) w raw_text.

    mapping: znak -> wartość enum
    default: wartość gdy żaden znak nie pasuje
    """

    def __init__(self, mapping: Dict[str, Any], default: Any = None) -> None:
        self.mapping = dict(mapping)
        self.default = default

    def parse(self, ctx: ColumnContext) -> Any:
        text = ctx.raw_text or ""
        for mark, value in self.mapping.items():
            if mark in text:
                return value
        return self.default
