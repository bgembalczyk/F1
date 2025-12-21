from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Callable, Iterable, TypeVar
from urllib.parse import urlparse

from bs4 import BeautifulSoup, Tag

# przypisy Wikipedii: [1], [b], [note 3], [citation needed], ...
_REF_RE = re.compile(r"\[\s*[^]]+\s*]")

T = TypeVar("T")


def clean_wiki_text(text: str) -> str:
    """
    Normalizacja whitespace + usunięcie przypisów Wikipedii.
    """
    t = text.replace("\xa0", " ").replace("&nbsp;", " ")
    t = _REF_RE.sub("", t)
    return t.strip()

def split_delimited_text(
    text: str | None, *, separators: str = r";|,|/", min_parts: int = 1
) -> list[str]:
    """Split text by common delimiters and trim whitespace.

    Returns an empty list for falsy input or when the number of non-empty parts is
    below ``min_parts``.
    """

    if not text:
        return []

    parts = [p.strip() for p in re.split(separators, text) if p.strip()]
    return parts if len(parts) >= min_parts else []

def _parse_number(
    text: str | None,
    *,
    pattern: str,
    cast: Callable[[str], T],
    group: int | str = 0,
    normalizers: Iterable[Callable[[str], str]] | None = None,
) -> T | None:
    """Generic helper for extracting numbers with regex and casting.

    ``pattern`` should contain the number either as the full match or a capturing
    group referenced by ``group``. ``normalizers`` are applied in order to the
    matched string before casting.
    """

    if not text:
        return None

    match = re.search(pattern, text)
    if not match:
        return None

    raw = match.group(group)
    for normalize in normalizers or []:
        raw = normalize(raw)

    try:
        return cast(raw)
    except (TypeError, ValueError):
        return None

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
    return _parse_number(
        text,
        pattern=r"[-+]?\d[\d,]*",
        cast=int,
        normalizers=(lambda s: s.replace(",", ""),),
    )

def parse_float_from_text(text: str) -> float | None:
    """
    Wyciąga pierwszą sensowną liczbę zmiennoprzecinkową z tekstu (ignoruje przecinki 1,234.5).
    """
    return _parse_number(
        text,
        pattern=r"[-+]?\d[\d,]*\.?\d*",
        cast=float,
        normalizers=(lambda s: s.replace(",", ""),),
    )

def parse_number_with_unit(text: str | None, *, unit: str) -> float | None:
    """Extract a float immediately followed by the given unit."""

    return _parse_number(
        text,
        pattern=rf"([-+]?[0-9][0-9,]*(?:\.[0-9]+)?)\s*{re.escape(unit)}",
        cast=float,
        group=1,
        normalizers=(lambda s: s.replace(",", ""),),
    )

def find_section_elements(
    soup: BeautifulSoup,
    section_id: str | None,
    target_tags: Iterable[str],
    **kwargs: Any,
) -> list[Tag]:
    """Find elements after a section heading or across the whole document.

    When ``section_id`` is provided, the search starts after the heading with
    the matching id. Otherwise, all matching elements in the soup are returned.
    Additional ``kwargs`` are forwarded to ``find_all`` / ``find_all_next``.
    """

    if section_id:
        heading = soup.find(id=section_id)
        if not heading:
            raise RuntimeError(f"Nie znaleziono sekcji o id={section_id!r}")

        return list(heading.find_all_next(target_tags, **kwargs))

    return list(soup.find_all(target_tags, **kwargs))

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
        text = clean_wiki_text(a.get_text(strip=True))

        if is_reference_link(a, allow_local_anchors=True):
            continue

        url = full_url(href)
        if is_wikipedia_redlink(url):
            url = None

        if is_language_marker_link(text, url):
            continue

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

    if any(cls in ("reference", "mw-cite-backlink") for cls in classes):
        return True

    if "cite_note" in href:
        return True

    if href.startswith("#"):
        text = clean_wiki_text(tag.get_text(" ", strip=True))
        return not text or not allow_local_anchors

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

def is_wikipedia_redlink(url: str | None) -> bool:
    """Return True for Wikipedia redlinks like ...&action=edit&redlink=1."""

    if not url:
        return False

    url_l = url.lower()
    return "wikipedia.org" in url_l and "action=edit" in url_l and "redlink=" in url_l

def is_language_marker_link(text: str | None, url: str | None) -> bool:
    """
    True tylko dla interwiki markerów typu:
    text='fr' i url='https://fr.wikipedia.org/wiki/...'
    """
    if not text or not url:
        return False

    txt = text.strip().lower()
    if not (2 <= len(txt) <= 3) or not txt.isalpha():
        return False

    try:
        host = (urlparse(url).hostname or "").lower()
    except Exception:
        return False

    # interesuje nas wyłącznie <lang>.wikipedia.org (ew. m.wikipedia.org też bywa)
    m = re.match(r"^([a-z]{2,3})\.(m\.)?wikipedia\.org$", host)
    if not m:
        return False

    lang = m.group(1)
    return txt == lang
