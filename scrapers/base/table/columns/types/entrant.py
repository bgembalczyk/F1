from __future__ import annotations

import re
from typing import Any

from bs4 import BeautifulSoup, Tag

from scrapers.base.helpers.links import normalize_links
from scrapers.base.helpers.text_normalization import clean_wiki_text
from scrapers.base.helpers.wiki import is_reference_link
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


class EntrantColumn(BaseColumn):
    """
    Parses entrant cells into a list of entries, one per <br> row.

    Each entry includes the full name text (without flags), a list of
    title sponsor links found in that row, and the license extracted
    from flag icons.
    """

    def parse(self, ctx: ColumnContext) -> Any:
        cell = ctx.cell
        if cell is None:
            return []

        segments = _split_cell_on_br(cell)
        link_lookup = _build_link_lookup(ctx.links or [])

        entrants: list[dict[str, Any]] = []
        for segment in segments:
            parsed = _parse_entrant_segment(segment, link_lookup)
            if parsed:
                entrants.append(parsed)

        return entrants


def _split_cell_on_br(cell: Tag) -> list[Tag]:
    html = cell.decode_contents()
    parts = re.split(r"<br\\s*/?>", html, flags=re.IGNORECASE)
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


def _build_link_lookup(links: list[dict[str, str | None]]):
    lookup: dict[str, list[dict[str, str | None]]] = {}
    for link in normalize_links(links, strip_marks=True, drop_empty=True):
        text = link.get("text") or ""
        if not text:
            continue
        lookup.setdefault(text, []).append(link)
    return lookup


def _parse_entrant_segment(
    segment: Tag,
    link_lookup: dict[str, list[dict[str, str | None]]],
) -> dict[str, Any] | None:
    license_info = _extract_licenses(segment, link_lookup)
    _strip_refs(segment)

    name = clean_wiki_text(segment.get_text(" ", strip=True))
    if not name:
        return None

    sponsors: list[dict[str, str | None]] = []
    for a in segment.find_all("a", href=True):
        if is_reference_link(a, allow_local_anchors=True):
            continue
        text = clean_wiki_text(a.get_text(strip=True))
        if not text:
            continue
        candidates = link_lookup.get(text)
        if candidates:
            sponsors.append(candidates[0])
        else:
            sponsors.append({"text": text, "url": None})

    record: dict[str, Any] = {"name": name, "title_sponsors": sponsors}
    if license_info is not None:
        record["license"] = license_info
    return record


def _extract_licenses(
    segment: Tag,
    link_lookup: dict[str, list[dict[str, str | None]]],
) -> dict[str, str | None] | None:
    licenses: list[dict[str, str | None]] = []
    for node in segment.select(".flagicon"):
        for a in node.find_all("a", href=True):
            text = clean_wiki_text(a.get_text(strip=True))
            if not text:
                continue
            candidates = link_lookup.get(text)
            if candidates:
                licenses.append(candidates[0])
            else:
                licenses.append({"text": text, "url": a.get("href")})
            break
        node.decompose()

    if not licenses:
        return None

    license_text = " / ".join(link.get("text") or "" for link in licenses).strip()
    license_url = " / ".join(
        link.get("url") or "" for link in licenses if link.get("url") is not None
    ).strip()
    return {
        "text": license_text,
        "url": license_url or None,
    }


def _strip_refs(segment: Tag) -> None:
    for sup in segment.find_all("sup", class_="reference"):
        sup.decompose()
