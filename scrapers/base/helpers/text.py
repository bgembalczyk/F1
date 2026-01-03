"""Text helper utilities shared across scrapers."""

import re
from typing import Callable

from bs4 import BeautifulSoup, Tag

from models.records.link import LinkRecord
from scrapers.base.helpers.constants import LANG_CODES, REF_RE


def _coerce_text(text: str | Tag | None) -> str:
    if isinstance(text, Tag):
        return text.get_text(" ", strip=True)
    return str(text or "")


# Centralne miejsce do usuwania przypisów wiki - nie duplikuj regexu w scraperach.

def _strip_wiki_refs(text: str) -> str:
    """Usuń przypisy w formacie [1], [note 3], ..."""
    return REF_RE.sub("", text)


def _normalize_dashes(text: str) -> str:
    """Ujednolić warianty myślników i usuń spacje wokół '-'."""
    t = text.replace("–", "-").replace("—", "-").replace("−", "-")
    return re.sub(r"(?<=\w)\s*-\s*(?=\w)", "-", t)


def _strip_lang_suffix(text: str) -> str:
    """Usuń tokeny językowe na końcu (np. "(es)", " es")."""
    lang_alt = "|".join(sorted(LANG_CODES, key=len, reverse=True))
    t = text

    while True:
        before = t

        # Usuń tokeny w nawiasach: (es), (fr), etc.
        t = re.sub(rf"\s*\(\s*({lang_alt})\s*\)\s*$", "", t, flags=re.IGNORECASE)
        t = t.strip()

        # Usuń tokeny bez nawiasów: " es", " fr", etc.
        t = re.sub(rf"\s+({lang_alt})\s*$", "", t, flags=re.IGNORECASE)
        t = t.strip()

        if t == before:
            break

    return t


def clean_wiki_text(
    text: str | Tag,
    *,
    strip_lang_suffix: bool = True,
    strip_refs: bool = True,
    normalize_dashes: bool = True,
) -> str:
    """Normalizuje whitespace oraz opcjonalnie usuwa przypisy i markery językowe."""
    t = _coerce_text(text).replace("\xa0", " ").replace("&nbsp;", " ")
    if strip_refs:
        t = _strip_wiki_refs(t)
    t = re.sub(r"\s+", " ", t).strip()
    if normalize_dashes:
        t = _normalize_dashes(t)
    if strip_lang_suffix:
        t = _strip_lang_suffix(t)
    return t


def strip_marks(text: str | Tag) -> str:
    """Usuwa typowe znaki oznaczeń z tabel."""
    return (
        _coerce_text(text)
        .replace("*", "")
        .replace("†", "")
        .replace("‡", "")
        .replace("✝", "")
        .replace("✚", "")
        .replace("~", "")
        .replace("^", "")
        .strip()
    )


def extract_links_from_cell(
    cell: str | Tag,
    *,
    full_url: Callable[[str], str] | None = None,
    allow_local_anchors: bool = True,
) -> list[LinkRecord]:
    """
    Zwraca listę linków {text, url} z komórki,
    ignorując przypisy (cite_note / reference).
    """
    if isinstance(cell, Tag):
        search_root = cell
    else:
        search_root = BeautifulSoup(cell or "", "html.parser")

    from scrapers.base.helpers.wiki import clean_link_record, is_reference_link

    links: list[LinkRecord] = []

    for a in search_root.find_all("a", href=True):
        href = str(a.get("href") or "")
        text = clean_wiki_text(a.get_text(strip=True))

        if is_reference_link(a, allow_local_anchors=allow_local_anchors):
            continue

        url: str | None = full_url(href) if full_url else href
        link: LinkRecord = {"text": text, "url": url}
        cleaned = clean_link_record(link)
        if cleaned:
            links.append(cleaned)

    return links
