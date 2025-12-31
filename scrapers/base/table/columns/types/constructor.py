from __future__ import annotations

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn
from scrapers.base.table.columns.types.constructor_part import ConstructorPartColumn


class ConstructorColumn(BaseColumn):
    def parse(self, ctx: ColumnContext):
        chassis = ConstructorPartColumn(0).parse(ctx)
        engine = ConstructorPartColumn(1).parse(ctx)
        data: dict[str, object] = {}
        if chassis is not None:
            data["chassis_constructor"] = chassis
        if engine is not None:
            data["engine_constructor"] = engine
        return data or None
