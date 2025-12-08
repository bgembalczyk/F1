from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Callable

from bs4 import Tag

# przypisy Wikipedii: [1], [b], [note 3], [citation needed], ...
_REF_RE = re.compile(r"\[\s*[^]]+\s*]")


def clean_wiki_text(text: str) -> str:
    """
    Normalizacja whitespace + usunięcie przypisów Wikipedii.
    """
    t = text.replace("\xa0", " ").replace("&nbsp;", " ")
    t = _REF_RE.sub("", t)
    return t.strip()


def parse_seasons(
    text: str, *, current_year: int | None = None
) -> list[dict[str, Any]]:
    """
    Zamienia tekst w stylu:
        '1973, 1975–1982, 1984'  lub '2014–present'
    na listę:
        [{"year": 1973, "url": ...}, {"year": 1975, "url": ...}, ..., {"year": 1984, "url": ...}]

    'present' (case-insensitive) → aktualny rok.
    """
    result: list[dict[str, Any]] = []
    seen: set[int] = set()

    if not text:
        return result

    if current_year is None:
        current_year = datetime.now().year

    # Zamień 'present' na aktualny rok (case-insensitive)
    text = re.sub(r"\bpresent\b", str(current_year), text, flags=re.IGNORECASE)

    parts = [p.strip() for p in text.split(",") if p.strip()]

    for part in parts:
        # zakres: 1975–1982 (en dash lub zwykły minus)
        m_range = re.fullmatch(r"(\d{4})\s*[\u2013-]\s*(\d{4})", part)
        if m_range:
            start = int(m_range.group(1))
            end = int(m_range.group(2))
            if end < start:
                start, end = end, start
            years = range(start, end + 1)
        else:
            # pojedynczy rok: 1973
            m_year = re.fullmatch(r"\d{4}", part)
            if not m_year:
                continue
            years = [int(part)]

        for y in years:
            if y in seen:
                continue
            seen.add(y)
            url = f"https://en.wikipedia.org/wiki/{y}_Formula_One_World_Championship"
            result.append({"year": y, "url": url})

    return result


def parse_int_from_text(text: str) -> int | None:
    """
    Wyciąga pierwszą sensowną liczbę całkowitą z tekstu (ignoruje przecinki 1,234).
    """
    if not text:
        return None
    m = re.search(r"[-+]?\d[\d,]*", text)
    if not m:
        return None
    num_str = m.group(0).replace(",", "")
    try:
        return int(num_str)
    except ValueError:
        return None


def parse_float_from_text(text: str) -> float | None:
    """
    Wyciąga pierwszą sensowną liczbę zmiennoprzecinkową z tekstu (ignoruje przecinki 1,234.5).
    """
    if not text:
        return None
    m = re.search(r"[-+]?\d[\d,]*\.?\d*", text)
    if not m:
        return None
    num_str = m.group(0).replace(",", "")
    try:
        return float(num_str)
    except ValueError:
        return None


def extract_links_from_cell(
    cell: Tag,
    *,
    full_url: Callable[[str | None], str | None],
) -> list[dict[str, Any]]:
    """
    Zwraca listę linków {text, url} z komórki,
    ignorując przypisy (cite_note / reference).
    """
    links: list[dict[str, Any]] = []

    for a in cell.find_all("a", href=True):
        href = a.get("href") or ""
        text = clean_wiki_text(a.get_text(" ", strip=True))

        if is_reference_link(a, allow_local_anchors=True):
            continue

        url = full_url(href)
        links.append({"text": text, "url": url})

    return links


def is_reference_link(tag: Tag, *, allow_local_anchors: bool = False) -> bool:
    """
    Sprawdza, czy ``<a>`` powinno być traktowane jako przypis/odnośnik techniczny.

    Kryteria:
    - ``href`` zawiera ``cite_note``;
    - klasa ``reference`` lub ``mw-cite-backlink``;
    - lokalne kotwice (``href`` zaczynające się od ``#``):
      - zawsze ignorowane gdy ``allow_local_anchors`` jest False;
      - ignorowane gdy tekst jest pusty nawet przy ``allow_local_anchors=True``.
    """

    href = tag.get("href") or ""
    classes = tag.get("class") or []

    if "cite_note" in href:
        return True

    if any(cls in ("reference", "mw-cite-backlink") for cls in classes):
        return True

    text = clean_wiki_text(tag.get_text(" ", strip=True))

    if href.startswith("#"):
        if not text or not allow_local_anchors:
            return True

    return False


def strip_marks(text: str | None) -> str | None:
    if text is None:
        return None
    # typowe znaki w tabelach F1
    return (
        text.replace("*", "")
        .replace("†", "")
        .replace("‡", "")
        .replace("✝", "")
        .replace("✚", "")
        .replace("~", "")
        .replace("^", "")
        .strip()
    )
