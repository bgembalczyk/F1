import re
from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.helpers.text import strip_marks
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.helpers.constants import MARKS_RE
from scrapers.base.table.columns.helpers.constants import SPLIT_RESULTS_RE
from scrapers.seasons.columns.helpers.constants import SPRINT_POINTS_START_YEAR
from scrapers.seasons.columns.helpers.race_result.superscript import (
    SuperscriptParseResult,
)

LETTER_RE = re.compile(r"[A-Za-z]")


class RaceResultCellParser:
    def extract_result_text(self, ctx: ColumnContext) -> str:
        cell = ctx.cell
        if cell is None:
            return (ctx.clean_text or "").strip()
        fragment = self._prepare_cell_fragment(cell)
        return clean_wiki_text(fragment.get_text(" ", strip=True))

    def parse_superscripts(
        self,
        ctx: ColumnContext,
        season_year: int | None,
    ) -> SuperscriptParseResult:
        cell = ctx.cell
        if cell is None:
            return self._empty_superscript_result()

        sup_texts, footnotes = self._collect_superscripts(cell)
        sprint_position, pole_position, fastest_lap = self._parse_superscript_tokens(
            sup_texts,
        )

        sprint_position, footnotes = self._normalize_sprint_position(
            sprint_position,
            footnotes,
            season_year,
        )
        pole_position, fastest_lap = self._enrich_marks_from_formatting(
            cell,
            pole_position=pole_position,
            fastest_lap=fastest_lap,
        )

        return SuperscriptParseResult(
            sprint_position=sprint_position,
            pole_position=pole_position,
            fastest_lap=fastest_lap,
            footnotes=footnotes,
        )

    def parse_results(self, text: str) -> list[dict[str, Any]]:
        return [
            self._parse_result_part(part)
            for part in self._split_result_parts(text)
        ]

    @staticmethod
    def _prepare_cell_fragment(cell: Any) -> BeautifulSoup:
        fragment = BeautifulSoup(str(cell), "html.parser")
        for span in fragment.find_all("span", style=True):
            style = "".join(span.get("style", "").split())
            if "position:absolute" in style:
                span.decompose()
        for sup in fragment.find_all("sup"):
            sup.decompose()
        return fragment

    @staticmethod
    def _empty_superscript_result() -> SuperscriptParseResult:
        return SuperscriptParseResult(
            sprint_position=None,
            pole_position=False,
            fastest_lap=False,
            footnotes=[],
        )

    @staticmethod
    def _normalize_sprint_position(
        sprint_position: int | None,
        footnotes: list[str],
        season_year: int | None,
    ) -> tuple[int | None, list[str]]:
        if season_year is None or season_year < SPRINT_POINTS_START_YEAR:
            return None, footnotes
        if sprint_position is None:
            return sprint_position, footnotes
        sprint_str = str(sprint_position)
        return sprint_position, [note for note in footnotes if note != sprint_str]

    @staticmethod
    def _enrich_marks_from_formatting(
        cell: Any,
        *,
        pole_position: bool,
        fastest_lap: bool,
    ) -> tuple[bool, bool]:
        if not pole_position and cell.find(["b", "strong"]):
            pole_position = True
        if not fastest_lap and cell.find(["i", "em"]):
            fastest_lap = True
        return pole_position, fastest_lap

    @staticmethod
    def _split_result_parts(text: str) -> list[str]:
        return [part.strip() for part in SPLIT_RESULTS_RE.split(text) if part.strip()]

    def _parse_result_part(self, part: str) -> dict[str, Any]:
        marks = MARKS_RE.findall(part)
        cleaned = strip_marks(part).strip()
        parenthesized, cleaned = self._unwrap_parenthesized(cleaned)

        result: dict[str, Any] = {"position": self._parse_position(cleaned)}
        if marks:
            result["marks"] = marks
        if parenthesized:
            result["points_counted"] = False
        return result

    @staticmethod
    def _unwrap_parenthesized(cleaned: str) -> tuple[bool, str]:
        parenthesized = cleaned.startswith("(") and cleaned.endswith(")")
        if parenthesized:
            return True, cleaned[1:-1].strip()
        return False, cleaned

    @staticmethod
    def _parse_position(cleaned: str) -> int | str | None:
        if not cleaned or cleaned in {"-", "--"}:
            return None
        if cleaned.isdigit():
            return int(cleaned)
        return cleaned

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
            for letter in LETTER_RE.findall(token):
                upper = letter.upper()
                if upper == "P":
                    pole_position = True
                elif upper == "F":
                    fastest_lap = True
            if token.isdigit() and sprint_position is None:
                sprint_position = int(token)

        return sprint_position, pole_position, fastest_lap
