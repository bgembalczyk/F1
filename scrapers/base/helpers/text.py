"""Text helper utilities shared across scrapers."""

import re
from typing import Callable

from bs4 import BeautifulSoup, Tag

from models.records.link import LinkRecord
from scrapers.base.helpers.constants import LANG_CODES, REF_RE


def coerce_text(text: str | Tag | None) -> str:
    if isinstance(text, Tag):
        return text.get_text(" ", strip=True)
    return str(text or "")


def extract_text_and_url(value: object) -> tuple[str, str]:
    if isinstance(value, dict):
        text = str(value.get("text") or value.get("name") or "").strip()
        url = str(value.get("url") or "").strip()
        return text, url
    if value is None:
        return "", ""
    return str(value).strip(), ""


def score_richer_entity(value: object) -> tuple[int, int]:
    text, url = extract_text_and_url(value)
    score = 0
    if text:
        score += 1
    if url:
        score += 2
    return score, len(text)


def choose_richer_entity(a: object, b: object) -> object:
    """
    Wybiera bogatszą encję (np. dict z url) między a i b.
    Preferuje encję z URL, potem z tekstem, a następnie dłuższy tekst.
    """
    if a is None:
        return b
    if b is None:
        return a

    score_a, len_a = score_richer_entity(a)
    score_b, len_b = score_richer_entity(b)

    if score_b > score_a:
        return b
    if score_a > score_b:
        return a
    if len_b > len_a:
        return b
    return a


# Centralne miejsce do usuwania przypisów wiki - nie duplikuj regexu w scraperach.


def strip_wiki_refs(text: str) -> str:
    """Usuń przypisy w formacie [1], [note 3], ..."""
    return REF_RE.sub("", text)


def normalize_dashes(text: str) -> str:
    """Ujednolić warianty myślników i usuń spacje wokół '-'."""
    t = text.replace("–", "-").replace("—", "-").replace("−", "-")
    return re.sub(r"(?<=\w)\s*-\s*(?=\w)", "-", t)


def strip_lang_suffix(text: str) -> str:
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
    # Store function references before parameters shadow them
    _normalize_dashes = globals()['normalize_dashes']
    _strip_lang_suffix = globals()['strip_lang_suffix']
    
    t = coerce_text(text).replace("\xa0", " ").replace("&nbsp;", " ")
    if strip_refs:
        t = strip_wiki_refs(t)
    t = re.sub(r"\s+", " ", t).strip()
    if normalize_dashes:
        t = _normalize_dashes(t)
    if strip_lang_suffix:
        t = _strip_lang_suffix(t)
    return t


def strip_marks(text: str | Tag) -> str:
    """Usuwa typowe znaki oznaczeń z tabel."""
    return (
        coerce_text(text)
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
    full_url: Callable[[str], str | None] | None = None,
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
