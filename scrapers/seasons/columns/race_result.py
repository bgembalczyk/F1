from typing import Any

from scrapers.base.table.columns.context import ColumnContext
import re

from bs4 import BeautifulSoup

from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.helpers.text import strip_marks
from scrapers.base.table.columns.helpers import extract_race_result_background
from scrapers.base.table.columns.helpers import parse_superscripts
from scrapers.base.table.columns.constants import MARKS_RE
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
    _CLASSIFIED_DNF_MARK = "†"
    _CLASSIFIED_DNF_NOTE = (
        "Driver did not finish the Grand Prix, but was classified as he completed more than 90% of the race distance."
    )
    _CLASSIFIED_DNF_BACKGROUNDS = {
        "Winner",
        "Second place",
        "Third place",
        "Other points position",
        "Other classified position",
    }
    _HALF_POINTS_MARK = "*"
    _HALF_POINTS_NOTE = (
        "Half points were awarded at this Grand Prix as less than 75% of the scheduled distance was completed. "
        "Fastest laps were not recognised in the final classification."
    )

    def parse(self, ctx: ColumnContext) -> Any:
        text = self._extract_result_text(ctx)
        if not text:
            return None

        sprint_position, pole_position, fastest_lap = parse_superscripts(ctx)
        background = self._map_background(extract_race_result_background(ctx))
        marks = MARKS_RE.findall(text)
        has_classified_dnf_mark = self._CLASSIFIED_DNF_MARK in marks

        position: int | str | None
        note: str | None = None
        if (
            has_classified_dnf_mark
            and background in self._CLASSIFIED_DNF_BACKGROUNDS
            and (strip_marks(text) or "").isdigit()
        ):
            position = int(strip_marks(text) or "")
            note = self._CLASSIFIED_DNF_NOTE
        else:
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
        if self._HALF_POINTS_MARK in ctx.header:
            payload["round_note"] = self._HALF_POINTS_NOTE
        if position is not None:
            payload["position"] = position
        if note:
            payload["position_note"] = note
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
        match = re.search(r"#?([0-9a-f]{6}|[0-9a-f]{3})", background, re.I)
        if not match:
            return None
        value = match.group(1).lower()
        if len(value) == 3:
            value = "".join(char * 2 for char in value)
        return self._BACKGROUND_TO_RESULT.get(value)
