from typing import Any

from scrapers.columns.types.base import BaseColumn
from scrapers.columns.types.context import ColumnContext
from scrapers.parsers.helpers import parse_entries_starts


class EntriesStartsColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> dict[str, Any]:
        entries, starts = parse_entries_starts(ctx)
        return {"entries": entries, "starts": starts}

    def apply(self, ctx: ColumnContext, record: dict[str, Any]) -> None:
        values = self.parse(ctx)
        for key, value in values.items():
            if ctx.model_fields is not None and key not in ctx.model_fields:
                continue
            record[key] = value
