"""Text helper utilities shared across scrapers."""

import re
from collections.abc import Callable

from bs4 import BeautifulSoup
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


def _is_language_link(text: str | None, url: str | None) -> bool:
    txt = (text or "").strip().lower()
    url_l = (url or "").strip().lower()
    return bool(txt and len(txt) in {2, 3} and f"://{txt}.wikipedia.org/" in url_l)


def _is_wikipedia_redlink(url: str | None) -> bool:
    normalized = (url or "").lower()
    return "redlink=1" in normalized and "w/index.php" in normalized


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
    if cell is None:
        return []

    cell_tag: Tag
    if isinstance(cell, str):
        soup = BeautifulSoup(cell, "html.parser")
        found = soup.find("td") or soup
        if not isinstance(found, Tag):
            return []
        cell_tag = found
    else:
        cell_tag = cell

    links: list[dict[str, str | None]] = []
    for anchor in cell_tag.find_all("a"):
        if not isinstance(anchor, Tag):
            continue
        text = clean_wiki_text(anchor.get_text(" ", strip=True))
        href = anchor.get("href")
        if not isinstance(href, str):
            continue
        if href.startswith("#cite_note-"):
            continue

        url = full_url(href) if full_url is not None else href
        if isinstance(url, str) and _is_language_link(text, url):
            continue
        if isinstance(url, str) and _is_wikipedia_redlink(url):
            url = None

        links.append({"text": text, "url": url})
    return links
