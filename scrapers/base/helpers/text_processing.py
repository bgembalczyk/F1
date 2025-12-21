"""Funkcje do normalizacji i porównywania tekstu."""

from __future__ import annotations
from typing import Any
import re


def safe_text(obj: Any) -> str:
    """Bezpieczna konwersja obiektu do znormalizowanego tekstu (lowercase, stripped)."""
    if isinstance(obj, dict):
        return (obj.get("text") or "").strip().lower()
    if obj is None:
        return ""
    return str(obj).strip().lower()


def norm_driver_text(obj: Any) -> str:
    """Normalizuje tekst kierowcy: usuwa dopiski w nawiasach i zbędne spacje."""
    s = safe_text(obj)
    if not s:
        return ""
    # usuń dopiski w nawiasach: "hailey (tum)" -> "hailey"
    s = re.sub(r"\s*\([^)]*\)\s*", " ", s)
    s = " ".join(s.split())
    return s


def driver_loose_match(a: Any, b: Any, *, min_len: int = 4) -> bool:
    """Porównuje kierowców z tolerancją na przedrostki i sufiksy."""
    da = norm_driver_text(a)
    db = norm_driver_text(b)
    if not da or not db:
        return False
    if len(da) < min_len or len(db) < min_len:
        return False
    return da == db or da.startswith(db) or db.startswith(da) or (da in db) or (db in da)


def norm_vehicle_text(v: Any) -> str:
    """Normalizuje tekst pojazdu."""
    if isinstance(v, dict):
        v = v.get("text") or ""
    s = str(v or "").strip().lower()
    s = " ".join(s.split())
    return s


def vehicle_prefix_match(a: Any, b: Any, *, min_len: int = 10) -> bool:
    """Porównuje pojazdy na podstawie prefiksu."""
    va = norm_vehicle_text(a)
    vb = norm_vehicle_text(b)
    if not va or not vb:
        return False
    if len(va) < min_len or len(vb) < min_len:
        return False
    return va.startswith(vb) or vb.startswith(va)


def add_name(names_set: set[str], name_list: list[str], value: str | None) -> None:
    """Dodaje nazwę do listy nazw, unikając duplikatów."""
    if not value:
        return
    value = value.strip()
    if value and value not in names_set:
        names_set.add(value)
        name_list.append(value)

