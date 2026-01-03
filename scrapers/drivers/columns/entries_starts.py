from typing import Any, Dict

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn
from scrapers.base.parsers.helpers import parse_entries_starts


class EntriesStartsColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Dict[str, Any]:
        entries, starts = parse_entries_starts(ctx)
        return {"entries": entries, "starts": starts}

    def apply(self, ctx: ColumnContext, record: Dict[str, Any]) -> None:
        values = self.parse(ctx)
        for key, value in values.items():
            if ctx.model_fields is not None and key not in ctx.model_fields:
                continue
            record[key] = value
