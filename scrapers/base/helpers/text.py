"""Text normalization and parsing helpers for scraper data."""

from __future__ import annotations

import re
from typing import Any


# ============================================================================
# Text Normalization
# ============================================================================


def normalize_text(obj: Any) -> str:
    """Bezpieczna konwersja obiektu do znormalizowanego tekstu (lowercase, stripped)."""
    if isinstance(obj, dict):
        return (obj.get("text") or "").strip().lower()
    if obj is None:
        return ""
    return str(obj).strip().lower()


def add_unique_name(
    names_set: set[str], name_list: list[str], value: str | None
) -> None:
    """Dodaje nazwę do listy nazw, unikając duplikatów."""
    if not value:
        return
    value = value.strip()
    if value and value not in names_set:
        names_set.add(value)
        name_list.append(value)


# ============================================================================
# Driver & Vehicle Matching
# ============================================================================


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
    return (
        da == db or da.startswith(db) or db.startswith(da) or (da in db) or (db in da)
    )


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


# ============================================================================
# Text Parsing
# ============================================================================


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
