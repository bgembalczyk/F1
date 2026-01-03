from typing import Any

from scrapers.base.table.columns.context import ColumnContext
import re

from bs4 import BeautifulSoup

from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.table.columns.helpers import extract_race_result_background
from scrapers.base.table.columns.helpers import parse_superscripts
from scrapers.base.table.columns.types.base import BaseColumn


class RaceResultColumn(BaseColumn):
    _BACKGROUND_TO_RESULT = {
        "ffffbf": "Winner",
        "dfdfdf": "Second place",
        "ffdf9f": "Third place",
        "dfffdf": "Other points position",
        "cfcfff": "Other classified position",
        "efcfff": "Not classified, retired",
        "ffcfcf": "Did not qualify",
        "000000": "Disqualified",
        "ffffff": "Did not start",
    }

    def parse(self, ctx: ColumnContext) -> Any:
        text = self._extract_result_text(ctx)
        if not text:
            return None

        sprint_position, pole_position, fastest_lap = parse_superscripts(ctx)
        background = self._map_background(extract_race_result_background(ctx))

        position: int | str | None
        if text == "-" or text == "–":
            position = None
        elif text.isdigit():
            position = int(text)
        else:
            position = text

        if position is None and background is None:
            return None

        payload: dict[str, Any] = {}
        if ctx.header_link and (ctx.header_link.get("url") or ctx.header_link.get("text")):
            round_link = dict(ctx.header_link)
            if not round_link.get("text"):
                round_link["text"] = ctx.header
            payload["round"] = round_link
        if position is not None:
            payload["position"] = position
        if sprint_position is not None:
            payload["sprint_position"] = sprint_position
        if pole_position:
            payload["pole_position"] = True
        if fastest_lap:
            payload["fastest_lap"] = True
        if background is not None:
            payload["background"] = background

        return payload or None

    @staticmethod
    def _extract_result_text(ctx: ColumnContext) -> str:
        cell = ctx.cell
        if cell is None:
            return (ctx.clean_text or "").strip()
        fragment = BeautifulSoup(str(cell), "html.parser")
        for sup in fragment.find_all("sup"):
            sup.decompose()
        return clean_wiki_text(fragment.get_text(" ", strip=True))

    def _map_background(self, background: str | None) -> str | None:
        if not background:
            return None
        match = re.search(r"#?([0-9a-f]{3}|[0-9a-f]{6})", background, re.I)
        if not match:
            return None
        value = match.group(1).lower()
        if len(value) == 3:
            value = "".join(char * 2 for char in value)
        return self._BACKGROUND_TO_RESULT.get(value)
