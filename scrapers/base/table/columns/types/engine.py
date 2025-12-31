from __future__ import annotations

import re
from typing import Any

from bs4 import BeautifulSoup, Tag

from models.records.link import LinkRecord
from scrapers.base.helpers.links import normalize_links
from scrapers.base.helpers.text_normalization import clean_wiki_text
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


class EngineColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        cell = ctx.cell
        if cell is None:
            return None

        segments = _split_cell_on_br(cell)
        link_lookup = _build_link_lookup(ctx.links or [])
        engines: list[dict[str, Any]] = []

        for segment in segments:
            engine = _parse_engine_segment(segment, link_lookup)
            if engine:
                engines.append(engine)

        if not engines:
            return None
        if len(engines) == 1:
            return engines[0]
        return engines


def _split_cell_on_br(cell: Tag) -> list[Tag]:
    html = cell.decode_contents()
    parts = re.split(r"<br\s*/?>", html, flags=re.IGNORECASE)
    segments: list[Tag] = []
    soup = cell.soup or BeautifulSoup("", "html.parser")

    for part in parts:
        if not part.strip():
            continue
        frag_soup = BeautifulSoup(part, "html.parser")
        span = soup.new_tag("span")
        for el in list(frag_soup.contents):
            span.append(el)
        segments.append(span)

    return segments or [cell]


def _build_link_lookup(links: list[LinkRecord]) -> dict[str, list[LinkRecord]]:
    lookup: dict[str, list[LinkRecord]] = {}
    for link in normalize_links(links, strip_marks=True, drop_empty=True):
        text = link.get("text") or ""
        if not text:
            continue
        lookup.setdefault(text, []).append(link)
    return lookup


def _parse_engine_segment(
    segment: Tag, link_lookup: dict[str, list[LinkRecord]]
) -> dict[str, Any] | None:
    raw_links: list[LinkRecord] = []
    for a in segment.find_all("a", href=True):
        text = clean_wiki_text(a.get_text(strip=True))
        if not text:
            continue
        candidates = link_lookup.get(text)
        if candidates:
            raw_links.append(candidates[0])
        else:
            raw_links.append({"text": text, "url": None})

    links = normalize_links(raw_links, strip_marks=True, drop_empty=True)
    clean_text = clean_wiki_text(segment.get_text(" ", strip=True))
    if not links and not clean_text:
        return None

    model: LinkRecord | None = links[0] if links else None

    displacement = _extract_displacement(clean_text)
    type_text = _extract_type_text(clean_text, displacement)
    layout, cylinders = _parse_engine_type(type_text)

    data: dict[str, Any] = {}
    if model:
        data["model"] = model
    if displacement:
        data["displacement_l"] = displacement
    if type_text:
        data["type"] = type_text
    if layout:
        data["layout"] = layout
    if cylinders is not None:
        data["cylinders"] = cylinders
    return data or None


def _extract_displacement(text: str) -> float | None:
    match = re.search(r"(\d+(?:\.\d+)?)\s*(?:L|litre|liter)s?\b", text, re.I)
    if not match:
        return None
    try:
        return float(match.group(1))
    except ValueError:
        return None


def _extract_type_text(text: str, displacement: float | None) -> str | None:
    if not text:
        return None
    cleaned = text
    cleaned = re.sub(r"(\d+(?:\.\d+)?)\s*(?:L|litre|liter)s?\b", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    match = re.search(
        r"\b(?:V\d{1,2}|W\d{1,2}|I\d{1,2}|H\d{1,2}|F\d{1,2}|Flat[-\s]?\d{1,2}|Straight[-\s]?\d{1,2})\b",
        cleaned,
        re.I,
    )
    if match:
        return match.group(0).replace(" ", "").replace("-", "")

    if displacement is None:
        match = re.search(r"\bV\d{1,2}\b", text, re.I)
        if match:
            return match.group(0)

    return None


def _parse_engine_type(type_text: str | None) -> tuple[str | None, int | None]:
    if not type_text:
        return None, None
    normalized = type_text.replace(" ", "").replace("-", "")
    match = re.match(r"([A-Za-z]+)(\d{1,2})$", normalized)
    if not match:
        return None, None
    layout = match.group(1).upper()
    try:
        cylinders = int(match.group(2))
    except ValueError:
        cylinders = None
    return layout, cylinders
