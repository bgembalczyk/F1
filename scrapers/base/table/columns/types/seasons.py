from typing import Any

from models.services.season_service import SeasonService
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


class SeasonsColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        return SeasonService.parse_seasons(ctx.clean_text)
