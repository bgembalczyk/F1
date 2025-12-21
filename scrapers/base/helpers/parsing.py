from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Callable, Iterable, TypeVar

T = TypeVar("T")


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
