from typing import Any
from typing import Dict
from typing import List

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn
from scrapers.drivers.helpers.parsers import parse_unit_list


class NestedUnitListColumn(BaseColumn):
    def __init__(self, subkey: str) -> None:
        self.subkey = subkey

    def parse(self, ctx: ColumnContext) -> List[Dict[str, Any]]:
        text = ctx.clean_text or ""
        return parse_unit_list(text)

    def apply(self, ctx: ColumnContext, record: Dict[str, Any]) -> None:
        if ctx.model_fields is not None and ctx.key not in ctx.model_fields:
            return
        value = self.parse(ctx)
        container = record.setdefault(ctx.key, {})
        container[self.subkey] = value
