from typing import Any

from scrapers.base.table.columns.context import ColumnContext
import re

from bs4 import BeautifulSoup

from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.helpers.text import strip_marks
from scrapers.base.table.columns.constants import MARKS_RE
from scrapers.base.table.columns.constants import SPLIT_RESULTS_RE
from scrapers.base.table.columns.helpers import extract_race_result_background
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
    _CLASSIFIED_DNF_NOTE = "classified_after_dnf_90_percent"
    _CLASSIFIED_DNF_START_YEAR = 1985
    _CLASSIFIED_DNF_BACKGROUNDS = {
        "Winner",
        "Second place",
        "Third place",
        "Other points position",
        "Other classified position",
    }
    _HALF_POINTS_NOTE = "half_points"
    _DOUBLE_POINTS_NOTE = "double_points"
    _F2_INELIGIBLE_YEARS = {1957, 1958, 1966, 1967, 1969}

    def __init__(self, *, season_year: int | None = None) -> None:
        self._season_year = season_year

    def parse(self, ctx: ColumnContext) -> Any:
        text = self._extract_result_text(ctx)
        if not text:
            return None

        sprint_position, pole_position, fastest_lap, footnotes = (
            self._parse_superscripts(ctx)
        )
        background = self._map_background(extract_race_result_background(ctx))

        results = self._parse_results(text)
        if not results and background is None:
            return None
        if background is None and all(result.get("position") is None for result in results):
            return None

        payload: dict[str, Any] = {}
        if ctx.header_link and (ctx.header_link.get("url") or ctx.header_link.get("text")):
            round_link = dict(ctx.header_link)
            if not round_link.get("text"):
                round_link["text"] = ctx.header
            round_note = self._round_note(ctx, round_link)
            if round_note:
                round_link.update(round_note)
            payload["round"] = round_link

        if results:
            share_count = len(results)
            if footnotes:
                for result in results:
                    result["footnotes"] = footnotes
            for result in results:
                self._apply_result_notes(result, background)
                if result.get("points_shared") and share_count > 1:
                    result["points_share_count"] = share_count
                result.pop("marks", None)
                # Add background, pole_position, and fastest_lap to each result
                if background is not None:
                    # Special case: NC with blue background means "Not classified, finished"
                    position = result.get("position")
                    if isinstance(position, str) and position.upper() == "NC" and background == "Other classified position":
                        result["background"] = "Not classified, finished"
                    else:
                        result["background"] = background
                if pole_position:
                    result["pole_position"] = True
                if fastest_lap:
                    result["fastest_lap"] = True
            payload["results"] = results
            # For backwards compatibility with shared fastest laps in driver standings
            if fastest_lap and len(results) > 1:
                payload["fastest_lap_shared"] = True
                payload["fastest_lap_share_count"] = len(results)
        if sprint_position is not None:
            payload["sprint_position"] = sprint_position
        if footnotes:
            payload["footnotes"] = footnotes

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

    def _parse_results(self, text: str) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for part in SPLIT_RESULTS_RE.split(text):
            part = part.strip()
            if not part:
                continue
            marks = MARKS_RE.findall(part)
            cleaned = strip_marks(part).strip()
            parenthesized = cleaned.startswith("(") and cleaned.endswith(")")
            if parenthesized:
                cleaned = cleaned[1:-1].strip()
            if not cleaned or cleaned in {"-", "–"}:
                position: int | str | None = None
            elif cleaned.isdigit():
                position = int(cleaned)
            else:
                position = cleaned
            result: dict[str, Any] = {"position": position}
            if marks:
                result["marks"] = marks
            if parenthesized:
                result["points_counted"] = False
            results.append(result)
        return results

    def _append_note(self, result: dict[str, Any], note: str) -> None:
        notes = result.setdefault("notes", [])
        if note not in notes:
            notes.append(note)

    def _apply_result_notes(
        self, result: dict[str, Any], background: str | None
    ) -> None:
        marks = result.get("marks") or []
        position = result.get("position")

        if (
            self._season_year is not None
            and self._season_year >= self._CLASSIFIED_DNF_START_YEAR
            and self._CLASSIFIED_DNF_MARK in marks
            and background in self._CLASSIFIED_DNF_BACKGROUNDS
            and isinstance(position, int)
        ):
            self._append_note(result, self._CLASSIFIED_DNF_NOTE)

        if "*" in marks and background == "Other classified position":
            result["points_eligible"] = False
            # Note: Don't add redundant note - points_eligible=false is sufficient
        if "~" in marks:
            result["points_eligible"] = False
            self._append_note(result, "shared_drive_no_points")
        if "‡" in marks and isinstance(position, int):
            result["points_eligible"] = False
            self._append_note(result, "no_points_awarded")

        if (
            self._season_year is not None
            and 1960 <= self._season_year <= 1964
            and "†" in marks
        ):
            result["shared_drive"] = True
            result["points_eligible"] = False
            self._append_note(result, "shared_drive_no_points")
        elif (
            self._season_year is not None
            and 1950 <= self._season_year <= 1957
            and "†" in marks
        ):
            result["shared_drive"] = True
            result["points_shared"] = True

        if (
            self._season_year is not None
            and self._season_year >= 1965
            and isinstance(position, str)
        ):
            status = position.lower()
            if status == "dns" and "†" in marks:
                self._append_note(result, "fatal_accident_before_race")
            elif status.startswith("ret") and ("†" in marks or "‡" in marks):
                self._append_note(result, "fatal_accident_during_race")

        if (
            self._season_year in self._F2_INELIGIBLE_YEARS
            and result.get("footnotes")
            and "1" in result["footnotes"]
        ):
            result["points_eligible"] = False
            self._append_note(result, "ineligible_f2")

    def _round_note(
        self, ctx: ColumnContext, round_link: dict[str, Any]
    ) -> dict[str, Any] | None:
        marks = MARKS_RE.findall(ctx.header)
        if not marks:
            return None
        header_text = strip_marks(ctx.header).strip()
        round_url = str(round_link.get("url") or "")
        if header_text == "500" or "Indianapolis_500" in round_url:
            return None
        if (
            self._season_year == 2014
            and "Abu_Dhabi_Grand_Prix" in round_url
            and "‡" in marks
        ):
            return {"note": self._DOUBLE_POINTS_NOTE, "points_multiplier": 2.0}
        if any(mark in {"*", "†", "‡"} for mark in marks):
            return {"note": self._HALF_POINTS_NOTE, "points_multiplier": 0.5}
        return None

    def _parse_superscripts(
        self, ctx: ColumnContext
    ) -> tuple[int | None, bool, bool, list[str]]:
        cell = ctx.cell
        if cell is None:
            return None, False, False, []

        sup_texts = []
        footnotes: list[str] = []
        for sup in cell.find_all("sup"):
            sup_text = clean_wiki_text(sup.get_text(" ", strip=True))
            if sup_text:
                sup_texts.append(sup_text)
                footnotes.extend(re.findall(r"\d+", sup_text))

        sprint_position = None
        pole_position = False
        fastest_lap = False

        for token in " ".join(sup_texts).split():
            letters = re.findall(r"[A-Za-z]", token)
            for letter in letters:
                upper = letter.upper()
                if upper == "P":
                    pole_position = True
                elif upper == "F":
                    fastest_lap = True
            if token.isdigit() and sprint_position is None:
                sprint_position = int(token)

        if self._season_year is None or self._season_year < 2021:
            sprint_position = None

        if not pole_position and cell.find(["b", "strong"]):
            pole_position = True
        if not fastest_lap and cell.find(["i", "em"]):
            fastest_lap = True

        return sprint_position, pole_position, fastest_lap, footnotes
