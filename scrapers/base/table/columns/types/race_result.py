from __future__ import annotations

import re
from typing import Any

from scrapers.base.helpers.text_normalization import clean_wiki_text
from scrapers.base.helpers.wiki import strip_marks
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn

_MARKS_RE = re.compile(r"[†‡✝✚*~^]")
_SPLIT_RESULTS_RE = re.compile(r"\s*/\s*")


class RaceResultColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        text = (ctx.clean_text or "").strip()
        if not text:
            return None

        results = _parse_results(text)
        if not results:
            return None

        sprint_position, pole_position, fastest_lap = _parse_superscripts(ctx)
        background = _extract_background(ctx)

        return {
            "results": results,
            "sprint_position": sprint_position,
            "pole_position": pole_position,
            "fastest_lap": fastest_lap,
            "background": background,
        }


def _parse_results(text: str) -> list[dict[str, Any]]:
    parts = _SPLIT_RESULTS_RE.split(text)
    results: list[dict[str, Any]] = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        marks = _MARKS_RE.findall(part)
        cleaned = strip_marks(part) or ""
        cleaned = cleaned.strip()
        value: int | str | None
        if not cleaned or cleaned == "-":
            value = None
        elif cleaned.isdigit():
            value = int(cleaned)
        else:
            value = cleaned
        results.append(
            {
                "value": value,
                "marks": marks or None,
            }
        )
    return results


def _parse_superscripts(ctx: ColumnContext) -> tuple[int | None, bool, bool]:
    cell = ctx.cell
    if cell is None:
        return None, False, False

    sup_texts = []
    for sup in cell.find_all("sup"):
        sup_text = clean_wiki_text(sup.get_text(" ", strip=True))
        if sup_text:
            sup_texts.append(sup_text)

    sprint_position = None
    pole_position = False
    fastest_lap = False

    for token in " ".join(sup_texts).split():
        if token.isdigit() and sprint_position is None:
            sprint_position = int(token)
            continue
        letters = re.findall(r"[A-Za-z]", token)
        for letter in letters:
            upper = letter.upper()
            if upper == "P":
                pole_position = True
            elif upper == "F":
                fastest_lap = True

    if not pole_position and cell.find(["b", "strong"]):
        pole_position = True
    if not fastest_lap and cell.find(["i", "em"]):
        fastest_lap = True

    return sprint_position, pole_position, fastest_lap


def _extract_background(ctx: ColumnContext) -> str | None:
    cell = ctx.cell
    if cell is None:
        return None

    style = cell.get("style") or ""
    if style:
        match = re.search(r"background(?:-color)?\s*:\s*([^;]+)", style, re.I)
        if match:
            return match.group(1).strip()

    bgcolor = cell.get("bgcolor")
    if bgcolor:
        return str(bgcolor).strip()

    return None
