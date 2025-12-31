from __future__ import annotations

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn
from models.services.rounds_service import RoundsService


class RoundsColumn(BaseColumn):
    def __init__(self, *, total_rounds: int | None = None) -> None:
        self.total_rounds = total_rounds

    def parse(self, ctx: ColumnContext):
        return RoundsService.parse_rounds(
            ctx.clean_text, total_rounds=self.total_rounds
        )
