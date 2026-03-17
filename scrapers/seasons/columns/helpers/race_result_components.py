import re
from dataclasses import dataclass
from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.helpers.text import strip_marks
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.helpers.constants import MARKS_RE
from scrapers.base.table.columns.helpers.constants import SPLIT_RESULTS_RE
from scrapers.seasons.columns.helpers.constants import SHORT_HEX_COLOR_LENGTH
from scrapers.seasons.columns.helpers.constants import SPRINT_POINTS_START_YEAR


@dataclass(frozen=True)
class SuperscriptParseResult:
    sprint_position: int | None
    pole_position: bool
    fastest_lap: bool
    footnotes: list[str]


class RaceResultCellParser:
    def extract_result_text(self, ctx: ColumnContext) -> str:
        cell = ctx.cell
        if cell is None:
            return (ctx.clean_text or "").strip()
        fragment = BeautifulSoup(str(cell), "html.parser")
        for span in fragment.find_all("span", style=True):
            style = "".join(span.get("style", "").split())
            if "position:absolute" in style:
                span.decompose()
        for sup in fragment.find_all("sup"):
            sup.decompose()
        return clean_wiki_text(fragment.get_text(" ", strip=True))

    def parse_superscripts(
        self,
        ctx: ColumnContext,
        season_year: int | None,
    ) -> SuperscriptParseResult:
        cell = ctx.cell
        if cell is None:
            return SuperscriptParseResult(
                sprint_position=None,
                pole_position=False,
                fastest_lap=False,
                footnotes=[],
            )

        sup_texts, footnotes = self._collect_superscripts(cell)
        sprint_position, pole_position, fastest_lap = self._parse_superscript_tokens(
            sup_texts,
        )

        if season_year is None or season_year < SPRINT_POINTS_START_YEAR:
            sprint_position = None
        elif sprint_position is not None:
            sprint_str = str(sprint_position)
            footnotes = [f for f in footnotes if f != sprint_str]

        if not pole_position and cell.find(["b", "strong"]):
            pole_position = True
        if not fastest_lap and cell.find(["i", "em"]):
            fastest_lap = True

        return SuperscriptParseResult(
            sprint_position=sprint_position,
            pole_position=pole_position,
            fastest_lap=fastest_lap,
            footnotes=footnotes,
        )

    def parse_results(self, text: str) -> list[dict[str, Any]]:
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


class RaceResultBackgroundMapper:
    def __init__(self, background_to_result: dict[str, str]) -> None:
        self._background_to_result = background_to_result

    def map(self, background: str | None) -> str | None:
        if not background:
            return None
        match = re.search(r"#?([0-9a-f]{6}|[0-9a-f]{3})", background, re.IGNORECASE)
        if not match:
            return None
        value = match.group(1).lower()
        if len(value) == SHORT_HEX_COLOR_LENGTH:
            value = "".join(char * 2 for char in value)
        return self._background_to_result.get(value)
