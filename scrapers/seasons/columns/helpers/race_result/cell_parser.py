import copy
import re
from typing import Any

from bs4 import NavigableString
from bs4 import Tag

from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.helpers.text import strip_marks
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.helpers.constants import MARKS_RE
from scrapers.base.table.columns.helpers.constants import SPLIT_RESULTS_RE
from scrapers.seasons.columns.helpers.constants import SPRINT_POINTS_START_YEAR
from scrapers.seasons.columns.helpers.race_result.superscript import (
    SuperscriptParseResult,
)

FOOTNOTE_RE = re.compile(r"\d+")
LETTER_RE = re.compile(r"[A-Za-z]")


class RaceResultCellParser:
    def extract_result_text(self, ctx: ColumnContext) -> str:
        cell = ctx.cell
        if cell is None:
            return (ctx.clean_text or "").strip()

        parts: list[str] = []
        self._extract_text_excluding_hidden(cell, parts)
        return clean_wiki_text(" ".join(parts))

    @staticmethod
    def _extract_text_excluding_hidden(node: Any, parts: list[str]) -> None:
        if isinstance(node, Tag):
            if node.name == "sup":
                return
            if node.name == "span" and node.has_attr("style"):
                style = "".join(node.get("style", "").split())
                if "position:absolute" in style:
                    return
            for child in node.children:
                RaceResultCellParser._extract_text_excluding_hidden(child, parts)
        elif type(node) is NavigableString:
            text = str(node).strip()
            if text:
                parts.append(text)

    def parse_superscripts(
        self,
        ctx: ColumnContext,
        season_year: int | None,
    ) -> SuperscriptParseResult:
        cell = ctx.cell
        if cell is None:
            return self._empty_superscript_result()

        sup_texts, footnotes, cell_pole, cell_fastest = (
            self._extract_superscripts_and_formatting(cell)
        )
        sprint_position, sup_pole, sup_fastest = self._parse_superscript_tokens(
            sup_texts,
        )

        sprint_position, footnotes = self._normalize_sprint_position(
            sprint_position,
            footnotes,
            season_year,
        )
        pole_position = sup_pole or cell_pole
        fastest_lap = sup_fastest or cell_fastest

        return SuperscriptParseResult(
            sprint_position=sprint_position,
            pole_position=pole_position,
            fastest_lap=fastest_lap,
            footnotes=footnotes,
        )

    def parse_results(self, text: str) -> list[dict[str, Any]]:
        return [
            self._parse_result_part(part) for part in self._split_result_parts(text)
        ]

    @staticmethod
    def _prepare_cell_fragment(cell: Any) -> Any:
        fragment = copy.deepcopy(cell)
        for element in fragment.find_all(["span", "sup"]):
            if element.name == "sup":
                element.decompose()
            elif element.name == "span":
                style = "".join(element.get("style", "").split())
                if "position:absolute" in style:
                    element.decompose()
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
    def _extract_superscripts_and_formatting(
        cell: Any,
    ) -> tuple[list[str], list[str], bool, bool]:
        sup_texts: list[str] = []
        footnotes: list[str] = []
        pole_position = False
        fastest_lap = False

        for tag in cell.find_all(["sup", "b", "strong", "i", "em"]):
            if tag.name == "sup":
                sup_text = clean_wiki_text(tag.get_text(" ", strip=True))
                if not sup_text:
                    continue
                sup_texts.append(sup_text)
                footnotes.extend(FOOTNOTE_RE.findall(sup_text))
            elif tag.name in ("b", "strong"):
                pole_position = True
            elif tag.name in ("i", "em"):
                fastest_lap = True

        return sup_texts, footnotes, pole_position, fastest_lap

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


__all__ = ["RaceResultCellParser"]