import re
from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.helpers.background import extract_race_result_background
from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.helpers.text import strip_marks
from scrapers.base.table.columns.constants import MARKS_RE
from scrapers.base.table.columns.constants import SPLIT_RESULTS_RE
from scrapers.base.table.columns.context import ColumnContext
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
    _SHARED_DRIVE_NO_POINTS_START_YEAR = 1960
    _SHARED_DRIVE_NO_POINTS_END_YEAR = 1964
    _SHARED_DRIVE_POINTS_START_YEAR = 1950
    _SHARED_DRIVE_POINTS_END_YEAR = 1957
    _FATAL_NOTES_START_YEAR = 1965
    _DOUBLE_POINTS_SEASON_YEAR = 2014
    _SPRINT_POINTS_START_YEAR = 2021
    _SHORT_HEX_COLOR_LENGTH = 3

    def __init__(self, *, season_year: int | None = None) -> None:
        self._season_year = season_year

    def parse(self, ctx: ColumnContext) -> Any:
        text = self._extract_result_text(ctx)
        if not text:
            return None

        sprint_position, pole_position, fastest_lap, footnotes = (
            self._parse_superscripts(ctx)
        )
        background = self._map_background(extract_race_result_background(ctx.cell))
        results = self._parse_results(text)

        if self._should_skip_payload(results, background):
            return None

        payload: dict[str, Any] = {}
        self._populate_round(payload, ctx)
        self._populate_results(
            payload,
            results,
            background,
            footnotes,
            pole_position=pole_position,
            fastest_lap=fastest_lap,
        )
        self._populate_payload_meta(payload, sprint_position, footnotes)
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

    @staticmethod
    def _should_skip_payload(
        results: list[dict[str, Any]],
        background: str | None,
    ) -> bool:
        if not results and background is None:
            return True
        return background is None and all(
            result.get("position") is None for result in results
        )

    def _populate_round(self, payload: dict[str, Any], ctx: ColumnContext) -> None:
        if not ctx.header_link:
            return
        if not (ctx.header_link.get("url") or ctx.header_link.get("text")):
            return

        round_link = dict(ctx.header_link)
        if not round_link.get("text"):
            round_link["text"] = ctx.header
        round_note = self._round_note(ctx, round_link)
        if round_note:
            round_link.update(round_note)
        payload["round"] = round_link

    def _populate_results(
        self,
        payload: dict[str, Any],
        results: list[dict[str, Any]],
        background: str | None,
        footnotes: list[str],
        *,
        pole_position: bool,
        fastest_lap: bool,
    ) -> None:
        if not results:
            return

        share_count = len(results)
        for result in results:
            if footnotes:
                result["footnotes"] = footnotes
            self._apply_result_notes(result, background)
            if result.get("points_shared") and share_count > 1:
                result["points_share_count"] = share_count
            result.pop("marks", None)
            self._apply_result_flags(
                result,
                background,
                pole_position=pole_position,
                fastest_lap=fastest_lap,
            )

        payload["results"] = results
        if fastest_lap and len(results) > 1:
            payload["fastest_lap_shared"] = True
            payload["fastest_lap_share_count"] = len(results)

    def _apply_result_flags(
        self,
        result: dict[str, Any],
        background: str | None,
        *,
        pole_position: bool,
        fastest_lap: bool,
    ) -> None:
        if background is not None:
            result["background"] = self._resolve_background(result, background)
        if pole_position:
            result["pole_position"] = True
        if fastest_lap:
            result["fastest_lap"] = True

    @staticmethod
    def _resolve_background(result: dict[str, Any], background: str) -> str:
        position = result.get("position")
        if (
            isinstance(position, str)
            and position.upper() == "NC"
            and background == "Other classified position"
        ):
            return "Not classified, finished"
        return background

    @staticmethod
    def _populate_payload_meta(
        payload: dict[str, Any],
        sprint_position: int | None,
        footnotes: list[str],
    ) -> None:
        if sprint_position is not None:
            payload["sprint_position"] = sprint_position
        if footnotes:
            payload["footnotes"] = footnotes

    def _map_background(self, background: str | None) -> str | None:
        if not background:
            return None
        match = re.search(r"#?([0-9a-f]{6}|[0-9a-f]{3})", background, re.IGNORECASE)
        if not match:
            return None
        value = match.group(1).lower()
        if len(value) == self._SHORT_HEX_COLOR_LENGTH:
            value = "".join(char * 2 for char in value)
        return self._BACKGROUND_TO_RESULT.get(value)

    def _parse_results(self, text: str) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for raw_part in SPLIT_RESULTS_RE.split(text):
            part = raw_part.strip()
            if not part:
                continue
            marks = MARKS_RE.findall(part)
            cleaned = strip_marks(part).strip()
            parenthesized = cleaned.startswith("(") and cleaned.endswith(")")
            if parenthesized:
                cleaned = cleaned[1:-1].strip()
            position = self._parse_position(cleaned)
            result: dict[str, Any] = {"position": position}
            if marks:
                result["marks"] = marks
            if parenthesized:
                result["points_counted"] = False
            results.append(result)
        return results

    @staticmethod
    def _parse_position(cleaned: str) -> int | str | None:
        if not cleaned or cleaned in {"-", "--"}:
            return None
        if cleaned.isdigit():
            return int(cleaned)
        return cleaned

    def _append_note(self, result: dict[str, Any], note: str) -> None:
        notes = result.setdefault("notes", [])
        if note not in notes:
            notes.append(note)

    def _apply_result_notes(
        self,
        result: dict[str, Any],
        background: str | None,
    ) -> None:
        marks = result.get("marks") or []
        position = result.get("position")
        self._apply_classified_dnf_notes(result, marks, position, background)
        self._apply_mark_notes(result, marks, position, background)
        self._apply_shared_drive_notes(result, marks)
        self._apply_fatal_accident_notes(result, marks, position)
        self._apply_f2_ineligible_notes(result)

    def _apply_classified_dnf_notes(
        self,
        result: dict[str, Any],
        marks: list[str],
        position: Any,
        background: str | None,
    ) -> None:
        if (
            self._season_year is not None
            and self._season_year >= self._CLASSIFIED_DNF_START_YEAR
            and self._CLASSIFIED_DNF_MARK in marks
            and background in self._CLASSIFIED_DNF_BACKGROUNDS
            and isinstance(position, int)
        ):
            self._append_note(result, self._CLASSIFIED_DNF_NOTE)

    def _apply_mark_notes(
        self,
        result: dict[str, Any],
        marks: list[str],
        position: Any,
        background: str | None,
    ) -> None:
        if "*" in marks and background == "Other classified position":
            result["points_eligible"] = False
        if "~" in marks:
            result["points_eligible"] = False
            self._append_note(result, "shared_drive_no_points")
        if "‡" in marks and isinstance(position, int):
            result["points_eligible"] = False
            self._append_note(result, "no_points_awarded")

    def _apply_shared_drive_notes(
        self,
        result: dict[str, Any],
        marks: list[str],
    ) -> None:
        if self._season_year is None or "†" not in marks:
            return

        if (
            self._SHARED_DRIVE_NO_POINTS_START_YEAR
            <= self._season_year
            <= self._SHARED_DRIVE_NO_POINTS_END_YEAR
        ):
            result["shared_drive"] = True
            result["points_eligible"] = False
            self._append_note(result, "shared_drive_no_points")
            return

        if (
            self._SHARED_DRIVE_POINTS_START_YEAR
            <= self._season_year
            <= self._SHARED_DRIVE_POINTS_END_YEAR
        ):
            result["shared_drive"] = True
            result["points_shared"] = True

    def _apply_fatal_accident_notes(
        self,
        result: dict[str, Any],
        marks: list[str],
        position: Any,
    ) -> None:
        if (
            self._season_year is None
            or self._season_year < self._FATAL_NOTES_START_YEAR
            or not isinstance(position, str)
        ):
            return

        status = position.lower()
        if status == "dns" and "†" in marks:
            self._append_note(result, "fatal_accident_before_race")
            return
        if status.startswith("ret") and ("†" in marks or "‡" in marks):
            self._append_note(result, "fatal_accident_during_race")

    def _apply_f2_ineligible_notes(self, result: dict[str, Any]) -> None:
        if self._season_year not in self._F2_INELIGIBLE_YEARS:
            return
        footnotes = result.get("footnotes")
        if footnotes and "1" in footnotes:
            result["points_eligible"] = False
            self._append_note(result, "ineligible_f2")

    def _round_note(
        self,
        ctx: ColumnContext,
        round_link: dict[str, Any],
    ) -> dict[str, Any] | None:
        marks = MARKS_RE.findall(ctx.header)
        if not marks:
            return None
        header_text = strip_marks(ctx.header).strip()
        round_url = str(round_link.get("url") or "")
        if header_text == "500" or "Indianapolis_500" in round_url:
            return None
        if (
            self._season_year == self._DOUBLE_POINTS_SEASON_YEAR
            and "Abu_Dhabi_Grand_Prix" in round_url
            and "‡" in marks
        ):
            return {"note": self._DOUBLE_POINTS_NOTE, "points_multiplier": 2.0}
        if any(mark in {"*", "†", "‡"} for mark in marks):
            return {"note": self._HALF_POINTS_NOTE, "points_multiplier": 0.5}
        return None

    def _parse_superscripts(
        self,
        ctx: ColumnContext,
    ) -> tuple[int | None, bool, bool, list[str]]:
        cell = ctx.cell
        if cell is None:
            return None, False, False, []

        sup_texts, footnotes = self._collect_superscripts(cell)
        sprint_position, pole_position, fastest_lap = self._parse_superscript_tokens(
            sup_texts,
        )

        if (
            self._season_year is None
            or self._season_year < self._SPRINT_POINTS_START_YEAR
        ):
            sprint_position = None

        if not pole_position and cell.find(["b", "strong"]):
            pole_position = True
        if not fastest_lap and cell.find(["i", "em"]):
            fastest_lap = True

        return sprint_position, pole_position, fastest_lap, footnotes

    @staticmethod
    def _collect_superscripts(cell: Any) -> tuple[list[str], list[str]]:
        sup_texts: list[str] = []
        footnotes: list[str] = []
        for sup in cell.find_all("sup"):
            sup_text = clean_wiki_text(sup.get_text(" ", strip=True))
            if not sup_text:
                continue
            sup_texts.append(sup_text)
            footnotes.extend(re.findall(r"\d+", sup_text))
        return sup_texts, footnotes

    @staticmethod
    def _parse_superscript_tokens(
        sup_texts: list[str],
    ) -> tuple[int | None, bool, bool]:
        sprint_position = None
        pole_position = False
        fastest_lap = False

        for token in " ".join(sup_texts).split():
            for letter in re.findall(r"[A-Za-z]", token):
                upper = letter.upper()
                if upper == "P":
                    pole_position = True
                elif upper == "F":
                    fastest_lap = True
            if token.isdigit() and sprint_position is None:
                sprint_position = int(token)

        return sprint_position, pole_position, fastest_lap
