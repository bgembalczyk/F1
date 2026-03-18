from models.services.rounds_service import parse_rounds
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


class RoundsColumn(BaseColumn):
    def __init__(self, *, total_rounds: int | None = None) -> None:
        self.total_rounds = total_rounds

    def parse(self, ctx: ColumnContext):
        return parse_rounds(
            ctx.clean_text,
            total_rounds=self.total_rounds,
        ).to_list()
