from __future__ import annotations

import re
from typing import Any

from bs4 import BeautifulSoup, Tag

from scrapers.base.helpers.links import normalize_links
from scrapers.base.helpers.text_normalization import clean_wiki_text
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn
from models.services.rounds_service import RoundsService


class DriversWithRoundsColumn(BaseColumn):
    def __init__(self, *, total_rounds: int | None = None) -> None:
        self.total_rounds = total_rounds

    def parse(self, ctx: ColumnContext) -> Any:
        cell = ctx.cell
        if cell is None:
            return []

        segments = _split_cell_on_br(cell)
        link_lookup = _build_link_lookup(ctx.links or [])

        drivers: list[dict[str, Any]] = []
        for segment in segments:
            parsed = _parse_driver_segment(
                segment, link_lookup, total_rounds=self.total_rounds
            )
            if parsed:
                drivers.append(parsed)

        return drivers


def _split_cell_on_br(cell: Tag) -> list[Tag]:
    html = cell.decode_contents()
    parts = re.split(r\"<br\\s*/?>\", html, flags=re.IGNORECASE)
    segments: list[Tag] = []
    soup = cell.soup or BeautifulSoup(\"\", \"html.parser\")

    for part in parts:
        if not part.strip():
            continue
        frag_soup = BeautifulSoup(part, \"html.parser\")
        span = soup.new_tag(\"span\")
        for el in list(frag_soup.contents):
            span.append(el)
        segments.append(span)

    return segments or [cell]


def _build_link_lookup(links: list[dict[str, str | None]]):
    lookup: dict[str, list[dict[str, str | None]]] = {}
    for link in normalize_links(links, strip_marks=True, drop_empty=True):
        text = link.get(\"text\") or \"\"
        if not text:
            continue
        lookup.setdefault(text, []).append(link)
    return lookup


def _parse_driver_segment(
    segment: Tag,
    link_lookup: dict[str, list[dict[str, str | None]]],
    *,
    total_rounds: int | None,
) -> dict[str, Any] | None:
    clean_text = clean_wiki_text(segment.get_text(\" \", strip=True))
    if not clean_text:
        return None

    rounds_text = _extract_rounds_text(clean_text)
    rounds = (
        RoundsService.parse_rounds(rounds_text, total_rounds=total_rounds)
        if rounds_text
        else []
    )
    number = _extract_number(clean_text)

    driver = _extract_driver(segment, link_lookup, clean_text)
    if not driver:
        return None

    record: dict[str, Any] = {\"driver\": driver}
    if number is not None:
        record[\"no\"] = number
    if rounds_text or rounds:
        record[\"rounds\"] = rounds
    return record


def _extract_driver(
    segment: Tag,
    link_lookup: dict[str, list[dict[str, str | None]]],
    clean_text: str,
) -> dict[str, str | None] | None:
    for a in segment.find_all(\"a\", href=True):
        text = clean_wiki_text(a.get_text(strip=True))
        if not text:
            continue
        candidates = link_lookup.get(text)
        if candidates:
            return candidates[0]
        return {\"text\": text, \"url\": None}

    cleaned = _strip_rounds_and_number(clean_text)
    if cleaned:
        return {\"text\": cleaned, \"url\": None}
    return None


def _extract_rounds_text(text: str) -> str | None:
    match = re.search(r\"\\(([^)]+)\\)\", text)
    if match:
        return match.group(1).strip()

    match = re.search(r\"Rounds?\\s*:?\\s*(.+)$\", text, re.I)
    if match:
        return match.group(1).strip()

    return None


def _extract_number(text: str) -> int | None:
    match = re.match(r\"^\\s*(\\d+)\\b\", text)
    if match:
        return int(match.group(1))

    match = re.search(r\"\\bNo\\.?\\s*(\\d+)\\b\", text, re.I)
    if match:
        return int(match.group(1))

    return None


def _strip_rounds_and_number(text: str) -> str:
    cleaned = re.sub(r\"\\(([^)]+)\\)\", \"\", text)
    cleaned = re.sub(r\"^\\s*\\d+\\b\", \"\", cleaned)
    cleaned = re.sub(r\"\\bNo\\.?\\s*\\d+\\b\", \"\", cleaned, flags=re.I)
    cleaned = re.sub(r\"Rounds?\\s*:?\\s*.+$\", \"\", cleaned, flags=re.I)
    cleaned = re.sub(r\"\\s+\", \" \", cleaned).strip(\" -–—\")
    return cleaned.strip()
