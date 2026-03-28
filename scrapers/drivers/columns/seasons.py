"""DOMAIN-SPECIFIC: drivers column rule.

(seasons parsing) localized for drivers domain.
"""

from typing import Any

from models.services.season_service import parse_seasons
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


class SeasonsColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        return [season.to_dict() for season in parse_seasons(ctx.clean_text)]
