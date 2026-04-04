"""Text helper utilities shared across scrapers."""

import re
from collections.abc import Callable

from bs4 import Tag

from scrapers.base.helpers.constants import LANG_SUFFIX_NO_PAREN_RE
from scrapers.base.helpers.constants import LANG_SUFFIX_PAREN_RE
from scrapers.base.helpers.constants import REF_RE


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
    t = text.replace("\u2013", "-").replace("\u2014", "-").replace("\u2212", "-")
    return re.sub(r"(?<=\w)\s*-\s*(?=\w)", "-", t)


def strip_lang_suffix(text: str) -> str:
    """Usuń tokeny językowe na końcu (np. "(es)", " es")."""
    t = text

    while True:
        before = t

        # Usuń tokeny w nawiasach: (es), (fr), etc.
        t = LANG_SUFFIX_PAREN_RE.sub("", t).strip()

        # Usuń tokeny bez nawiasów: " es", " fr", etc.
        t = LANG_SUFFIX_NO_PAREN_RE.sub("", t).strip()

        if t == before:
            break

    return t


# Store references to avoid shadowing in clean_wiki_text
_normalize_dashes_func = normalize_dashes
_strip_lang_suffix_func = strip_lang_suffix


def clean_wiki_text(
    text: str | Tag,
    *,
    strip_lang_suffix: bool = True,
    strip_refs: bool = True,
    normalize_dashes: bool = True,
) -> str:
    """Normalizuje whitespace oraz opcjonalnie usuwa przypisy i markery językowe."""
    t = coerce_text(text).replace("\xa0", " ").replace("&nbsp;", " ")
    if strip_refs:
        t = strip_wiki_refs(t)
    t = re.sub(r"\s+", " ", t).strip()
    if normalize_dashes:
        t = _normalize_dashes_func(t)
    if strip_lang_suffix:
        t = _strip_lang_suffix_func(t)
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
    cell: Tag | str | None,
    *,
    full_url: Callable[[str], str | None] | None = None,
) -> list[dict[str, str | None]]:
    """Backward-compatible helper for extracting normalized links from table cells."""
    # di-antipattern-allow: local import avoids a hot-path circular dependency.
    from scrapers.base.helpers.links import normalize_links

    return normalize_links(
        cell,
        full_url=full_url,
        drop_empty=True,
        strip_lang_suffix=True,
    )
