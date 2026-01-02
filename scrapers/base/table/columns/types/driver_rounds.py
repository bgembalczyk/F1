from __future__ import annotations

import re
from typing import Any

from bs4 import BeautifulSoup, Tag

from scrapers.base.helpers.links import normalize_links
from scrapers.base.helpers.text_normalization import clean_wiki_text
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.helpers import build_driver_link_lookup
from scrapers.base.table.columns.helpers import parse_driver_segment
from scrapers.base.table.columns.helpers import split_cell_on_br
from scrapers.base.table.columns.types.base import BaseColumn
from models.services.rounds_service import RoundsService


class DriversWithRoundsColumn(BaseColumn):
    def __init__(self, *, total_rounds: int | None = None) -> None:
        self.total_rounds = total_rounds

    def parse(self, ctx: ColumnContext) -> Any:
        cell = ctx.cell
        if cell is None:
            return []

        segments = split_cell_on_br(cell)
        link_lookup = build_driver_link_lookup(ctx.links or [])

        drivers: list[dict[str, Any]] = []
        for segment in segments:
            parsed = parse_driver_segment(
                segment, link_lookup, total_rounds=self.total_rounds
            )
            if parsed:
                drivers.append(parsed)

        return drivers

