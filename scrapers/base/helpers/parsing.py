from __future__ import annotations

import re
from typing import Callable, TypeVar, Iterable

T = TypeVar("T")


# ============================================================================
# Text Parsing
# ============================================================================


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
