"""Time and date normalization helpers for record data."""

from __future__ import annotations

import re
from typing import Any


from scrapers.base.helpers.value_objects import NormalizedTime


def _extract_time_value(value: Any) -> tuple[str | None, float | None]:
    """
    Zwraca (text, seconds) z różnych reprezentacji:
    - NormalizedTime(text, seconds)
    - dict {"text": ..., "seconds": ...}
    - number -> (None, float)
    - string -> (string, None)
    """
    if NormalizedTime is not None and isinstance(value, NormalizedTime):
        return value.text, value.seconds

    if isinstance(value, dict):
        text = value.get("text")
        seconds = value.get("seconds")
        sec = float(seconds) if isinstance(seconds, (int, float)) else None
        txt = str(text).strip() if text is not None else None
        return (txt or None), sec

    if isinstance(value, (int, float)):
        return None, float(value)

    if value is not None:
        return str(value), None

    return None, None


def parse_time_key(rec: dict[str, Any]) -> float | str | None:
    """
    Normalizuje time do postaci klucza:
    - jeśli mamy seconds -> używamy seconds (float)
    - jeśli mamy tekst, próbujemy sparsować MM:SS.xxx -> sekundy
    - jak się nie uda, używamy znormalizowanego tekstu
    """
    t = rec.get("time")

    txt, seconds = _extract_time_value(t)
    if seconds is not None:
        return seconds

    if not txt:
        return None

    s = txt.strip()

    m = re.match(r"(?:(\d+):)?(\d+(?:\.\d+)?)", s)
    if m:
        minutes = int(m.group(1)) if m.group(1) else 0
        sec = float(m.group(2))
        return minutes * 60 + sec

    return s.lower()


def parse_time_seconds(rec: dict[str, Any]) -> float | None:
    """
    Zwraca czas WYŁĄCZNIE jako sekundy (float) albo None.
    Obsługuje:
    - rec["time_seconds"] (jeśli istnieje)
    - rec["time"] jako liczba
    - rec["time"] jako dict {"seconds": ...}
    - rec["time"] jako tekst: "M:SS.xxx" albo "SS.xxx"
    - rec["time"] jako NormalizedTime
    """
    ts = rec.get("time_seconds")
    if isinstance(ts, (int, float)):
        return float(ts)

    t = rec.get("time")
    txt, seconds = _extract_time_value(t)
    if seconds is not None:
        return seconds

    if txt is None:
        return None

    s = str(txt).strip()
    if not s:
        return None

    m = re.match(r"^(?:(\d+):)?(\d+(?:\.\d+)?)$", s)
    if not m:
        return None

    minutes = int(m.group(1)) if m.group(1) else 0
    sec = float(m.group(2))
    return minutes * 60.0 + sec


def normalize_time_value(rec: dict[str, Any]) -> None:
    """
    Zamienia time dict/NormalizedTime na float jeśli jest seconds,
    albo próbuje sparsować tekstowo.

    UWAGA: jeśli time jest już liczbą/str, zostawiamy jak jest (jak w main).
    """
    t = rec.get("time")

    if not (
        isinstance(t, dict)
        or (NormalizedTime is not None and isinstance(t, NormalizedTime))
    ):
        return

    txt, seconds = _extract_time_value(t)
    if seconds is not None:
        rec["time"] = seconds
        return

    if not txt:
        rec["time"] = None
        return

    m = re.match(r"(?:(\d+):)?(\d+\.\d+|\d+)", txt.strip())
    if m:
        minutes = int(m.group(1)) if m.group(1) else 0
        sec = float(m.group(2))
        rec["time"] = minutes * 60 + sec
    else:
        rec["time"] = txt


def normalize_date_value(rec: dict[str, Any]) -> None:
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
