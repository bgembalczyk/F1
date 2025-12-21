"""Funkcje do przetwarzania i parsowania czasu."""

from __future__ import annotations
from typing import Any
import re


def time_key(rec: dict[str, Any]) -> float | str | None:
    """
    Normalizuje time do postaci klucza:
    - jeśli mamy seconds -> używamy seconds (float)
    - jeśli mamy tekst, próbujemy sparsować MM:SS.xxx -> sekundy
    - jak się nie uda, używamy znormalizowanego tekstu
    """
    t = rec.get("time")

    # jeśli to już liczba (po naszym cleanupie), użyj bezpośrednio
    if isinstance(t, (int, float)):
        return float(t)

    txt: str | None = None

    if isinstance(t, dict):
        if "seconds" in t and isinstance(t["seconds"], (int, float)):
            return float(t["seconds"])
        txt = t.get("text")
    elif t is not None:
        txt = str(t)

    if not txt:
        return None

    s = txt.strip()

    # spróbuj sparsować MM:SS.xxx
    m = re.match(r"(?:(\d+):)?(\d+(?:\.\d+)?)", s)
    if m:
        minutes = int(m.group(1)) if m.group(1) else 0
        seconds = float(m.group(2))
        return minutes * 60 + seconds

    # fallback – traktujemy jako tekstowy klucz
    return s.lower()


def time_seconds(rec: dict[str, Any]) -> float | None:
    """
    Zwraca czas WYŁĄCZNIE jako sekundy (float) albo None.
    Obsługuje:
    - rec["time_seconds"] (jeśli istnieje)
    - rec["time"] jako liczba
    - rec["time"] jako dict {"seconds": ...}
    - rec["time"] jako tekst: "M:SS.xxx" albo "SS.xxx"
    """
    # 1) jeśli masz już time_seconds – traktuj jako prawdę
    ts = rec.get("time_seconds")
    if isinstance(ts, (int, float)):
        return float(ts)

    t = rec.get("time")

    # 2) liczba
    if isinstance(t, (int, float)):
        return float(t)

    # 3) dict z seconds
    if isinstance(t, dict):
        sec = t.get("seconds")
        if isinstance(sec, (int, float)):
            return float(sec)
        txt = t.get("text")
    else:
        txt = t

    if txt is None:
        return None

    s = str(txt).strip()
    if not s:
        return None

    # 4) parsuj "M:SS.xxx" lub "SS.xxx"
    m = re.match(r"^(?:(\d+):)?(\d+(?:\.\d+)?)$", s)
    if not m:
        return None

    minutes = int(m.group(1)) if m.group(1) else 0
    seconds = float(m.group(2))
    return minutes * 60.0 + seconds


def simplify_time(rec: dict[str, Any]) -> None:
    """Zamienia time dict na float jeśli jest seconds, albo próbuje sparsować tekstowo."""
    t = rec.get("time")
    if not isinstance(t, dict):
        return

    if "seconds" in t:
        rec["time"] = t["seconds"]
        return

    txt = t.get("text")
    if not txt:
        rec["time"] = None
        return

    m = re.match(r"(?:(\d+):)?(\d+\.\d+|\d+)", txt.strip())
    if m:
        minutes = int(m.group(1)) if m.group(1) else 0
        seconds = float(m.group(2))
        rec["time"] = minutes * 60 + seconds
    else:
        rec["time"] = txt


def simplify_date(rec: dict[str, Any]) -> None:
    """Zamienia date dict na wartość "YYYY-MM-DD" lub "YYYY-MM" lub "YYYY"."""
    d = rec.get("date")
    if not isinstance(d, dict):
        return
    iso = d.get("iso")
    if iso:
        rec["date"] = iso
    else:
        txt = d.get("text")
        if txt:
            rec["date"] = txt.strip()

