"""Text normalization and parsing helpers for scraper data."""

from __future__ import annotations

from datetime import datetime
import re
from typing import Any, Callable, Iterable, TypeVar

_REF_RE = re.compile(r"\[\s*[^]]+\s*]")

T = TypeVar("T")


def normalize_text(obj: Any) -> str:
    """Bezpieczna konwersja obiektu do znormalizowanego tekstu (lowercase, stripped)."""
    if isinstance(obj, dict):
        return (obj.get("text") or "").strip().lower()
    if obj is None:
        return ""
    return str(obj).strip().lower()


def normalize_driver_text(obj: Any) -> str:
    """Normalizuje tekst kierowcy: usuwa dopiski w nawiasach i zbędne spacje."""
    s = normalize_text(obj)
    if not s:
        return ""
    s = re.sub(r"\s*\([^)]*\)\s*", " ", s)
    return " ".join(s.split())


def match_driver_loose(a: Any, b: Any, *, min_len: int = 4) -> bool:
    """Porównuje kierowców z tolerancją na przedrostki i sufiksy."""
    da = normalize_driver_text(a)
    db = normalize_driver_text(b)
    if not da or not db:
        return False
    if len(da) < min_len or len(db) < min_len:
        return False
    return da == db or da.startswith(db) or db.startswith(da) or (da in db) or (db in da)


def normalize_vehicle_text(v: Any) -> str:
    """Normalizuje tekst pojazdu."""
    if isinstance(v, dict):
        v = v.get("text") or ""
    s = str(v or "").strip().lower()
    return " ".join(s.split())


def match_vehicle_prefix(a: Any, b: Any, *, min_len: int = 10) -> bool:
    """Porównuje pojazdy na podstawie prefiksu."""
    va = normalize_vehicle_text(a)
    vb = normalize_vehicle_text(b)
    if not va or not vb:
        return False
    if len(va) < min_len or len(vb) < min_len:
        return False
    return va.startswith(vb) or vb.startswith(va)


def add_unique_name(names_set: set[str], name_list: list[str], value: str | None) -> None:
    """Dodaje nazwę do listy nazw, unikając duplikatów."""
    if not value:
        return
    value = value.strip()
    if value and value not in names_set:
        names_set.add(value)
        name_list.append(value)


def clean_wiki_text(text: str) -> str:
    """Normalizuje whitespace i usuwa przypisy Wikipedii."""
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
    """Generic helper for extracting numbers with regex and casting."""
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

    text = re.sub(r"\bpresent\b", str(current_year), text, flags=re.IGNORECASE)
    parts = [p.strip() for p in text.split(",") if p.strip()]

    for part in parts:
        m_range = re.fullmatch(r"(\d{4})\s*[\u2013-]\s*(\d{4})", part)
        if m_range:
            start = int(m_range.group(1))
            end = int(m_range.group(2))
            if end < start:
                start, end = end, start
            years = range(start, end + 1)
        else:
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
    """Wyciąga pierwszą sensowną liczbę całkowitą z tekstu (ignoruje przecinki 1,234)."""
    return _parse_number(
        text,
        pattern=r"[-+]?\d[\d,]*",
        cast=int,
        normalizers=(lambda s: s.replace(",", ""),),
    )


def parse_float_from_text(text: str) -> float | None:
    """Wyciąga pierwszą sensowną liczbę zmiennoprzecinkową z tekstu (ignoruje przecinki 1,234.5)."""
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


def strip_marks(text: str | None) -> str | None:
    """Usuwa typowe znaki oznaczeń z tabel."""
    if text is None:
        return None
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
