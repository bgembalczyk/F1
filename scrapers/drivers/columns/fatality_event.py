from typing import Any

from scrapers.base.helpers.links import normalize_links
from scrapers.base.helpers.wiki import strip_marks
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.base import BaseColumn


class FatalityEventColumn(BaseColumn):
    def __init__(self, auto_column: AutoColumn | None = None) -> None:
        self.auto_column = auto_column or AutoColumn()

    def parse(self, ctx: ColumnContext) -> Any:
        championship = "†" not in (ctx.raw_text or "")
        auto_value = self.auto_column.parse(ctx)
        if isinstance(auto_value, dict):
            cleaned = dict(auto_value)
            cleaned["text"] = strip_marks(cleaned.get("text")) or ""
            return {"event": cleaned, "championship": championship}
        if isinstance(auto_value, list):
            return {
                "event": normalize_links(auto_value, strip_marks=True, drop_empty=True),
                "championship": championship,
            }
        if isinstance(auto_value, str):
            return {"event": strip_marks(auto_value), "championship": championship}
        return {"event": auto_value, "championship": championship}
