from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scrapers.base.table.columns.context import ColumnContext


class ConstructorColumn:
    """Backward-compatible parser splitting constructor links into chassis/engine."""

    def parse(self, ctx: ColumnContext) -> dict[str, object]:
        links = list(ctx.links or [])
        if not links:
            return {"chassis_constructor": None, "engine_constructor": None}

        chassis = links[0]
        engine = links[1] if len(links) > 1 else chassis
        return {
            "chassis_constructor": chassis,
            "engine_constructor": engine,
        }
