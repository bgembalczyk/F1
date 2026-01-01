from __future__ import annotations

from scrapers.base.helpers.links import normalize_links
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn
from scrapers.base.table.columns.types.constructor_part import ConstructorPartColumn


class ConstructorColumn(BaseColumn):
    def parse(self, ctx: ColumnContext):
        normalized_links = normalize_links(ctx.links, strip_marks=True, drop_empty=True)
        has_line_break = ctx.cell.find("br") is not None if ctx.cell else False
        if (
            has_line_break
            and "-" not in (ctx.clean_text or "")
            and len(normalized_links) >= 2
        ):
            return {
                "chassis_constructor": normalized_links,
                "engine_constructor": normalized_links,
            }
        chassis = ConstructorPartColumn(0).parse(ctx)
        engine = ConstructorPartColumn(1).parse(ctx)
        data: dict[str, object] = {}
        if chassis is not None:
            data["chassis_constructor"] = chassis
        if engine is not None:
            data["engine_constructor"] = engine
        return data or None
