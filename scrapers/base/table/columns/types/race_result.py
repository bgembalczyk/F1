from __future__ import annotations

import re
from typing import Any

from scrapers.base.helpers.text_normalization import clean_wiki_text
from scrapers.base.helpers.wiki import strip_marks
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.helpers import extract_race_result_background
from scrapers.base.table.columns.helpers import parse_results
from scrapers.base.table.columns.helpers import parse_superscripts
from scrapers.base.table.columns.types.base import BaseColumn



class RaceResultColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        text = (ctx.clean_text or "").strip()
        if not text:
            return None

        results = parse_results(text)
        if not results:
            return None

        sprint_position, pole_position, fastest_lap = parse_superscripts(ctx)
        background = extract_race_result_background(ctx)

        return {
            "results": results,
            "sprint_position": sprint_position,
            "pole_position": pole_position,
            "fastest_lap": fastest_lap,
            "background": background,
        }


