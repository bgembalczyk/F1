"""Time and date normalization helpers for record data."""

from __future__ import annotations

import re
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Any


from scrapers.base.helpers.value_objects import NormalizedTime


_TIME_SECONDS_RE = re.compile(r"^\s*(?:(\d+):)?(\d+(?:\.\d+)?)\s*$")
_TIME_KEY_RE = re.compile(r"(?:(\d+):)?(\d+(?:\.\d+)?)")
_DATE_RANGE_SPLIT = re.compile(r"\s*[–-]\s*")
_DATE_FORMATS = [
    "%d %B %Y",  # 7 June 2019
    "%d %b %Y",  # 7 Jun 2019
    "%B %d, %Y",  # June 7, 2019
    "%b %d, %Y",  # Jun 7, 2019
]


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


def _seconds_from_match(match: re.Match[str]) -> float:
    minutes_raw = match.group(1)
    seconds_raw = match.group(2)

    minutes = int(minutes_raw) if minutes_raw else 0
    seconds_dec = Decimal(seconds_raw)
    total = Decimal(minutes * 60) + seconds_dec

    if "." in seconds_raw:
        places = len(seconds_raw.split(".", 1)[1])
        quant = Decimal("1." + ("0" * places))
        total = total.quantize(quant, rounding=ROUND_HALF_UP)

    return float(total)


def parse_time_seconds_from_text(value: Any) -> float | None:
    """
    Zwraca sekundy (float) z różnych reprezentacji czasu:
    - NormalizedTime(text, seconds)
    - dict {"text": ..., "seconds": ...}
    - number -> float
    - string -> "M:SS.xxx" albo "SS.xxx"
    """
    txt, seconds = _extract_time_value(value)
    if seconds is not None:
        return seconds

    if txt is None:
        return None

    s = str(txt).strip()
    if not s:
        return None

    match = _TIME_SECONDS_RE.match(s)
    if not match:
        return None

    return _seconds_from_match(match)


def parse_time_text(value: Any) -> str | None:
    txt, _ = _extract_time_value(value)
    if txt is None:
        return None
    s = str(txt).strip()
    return s or None


def _clean_date_base(text: str) -> str:
    base = text.split("(", 1)[0].strip()
    parts = _DATE_RANGE_SPLIT.split(base)
    if len(parts) > 1:
        first = parts[0].strip()
        tail = parts[-1].strip()
        if any(ch.isalpha() for ch in tail):
            base = f"{first} {tail}"
        else:
            base = parts[0].strip()
    return base


def _parse_date_iso(base: str) -> str | None:
    for fmt in _DATE_FORMATS:
        try:
            dt = datetime.strptime(base, fmt)
            return dt.date().isoformat()
        except ValueError:
            continue

    for fmt in ("%B %Y", "%b %Y"):
        try:
            dt = datetime.strptime(base, fmt)
            return dt.strftime("%Y-%m")
        except ValueError:
            continue

    if re.fullmatch(r"\d{4}", base):
        return base

    return None


def parse_date_text(text: str) -> dict[str, Any]:
    stripped = text.strip() if text else ""
    if not stripped:
        return {"text": None, "iso": None, "years": None}

    iso_full = re.findall(r"\d{4}-\d{2}-\d{2}", stripped)
    iso_month = re.findall(r"\d{4}-\d{2}", stripped)
    years = re.findall(r"\b(1[89]\d{2}|20\d{2})\b", stripped)

    iso: str | list[str] | None = None
    if iso_full:
        iso = iso_full
    elif iso_month:
        iso = iso_month

    if iso is None:
        base = _clean_date_base(stripped)
        iso = _parse_date_iso(base)

    return {
        "text": stripped or None,
        "iso": iso,
        "years": years or None,
    }


def parse_time_key(rec: dict[str, Any]) -> float | str | None:
    """
    Normalizuje time do postaci klucza:
    - jeśli mamy seconds -> używamy seconds (float)
    - jeśli mamy tekst, próbujemy sparsować MM:SS.xxx -> sekundy
    - jak się nie uda, używamy znormalizowanego tekstu
    """
    t = rec.get("time")

    seconds = parse_time_seconds_from_text(t)
    if seconds is not None:
        return seconds

    txt = parse_time_text(t)
    if not txt:
        return None

    s = txt.strip()

    m = _TIME_KEY_RE.match(s)
    if m:
        return _seconds_from_match(m)

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
    return parse_time_seconds_from_text(t)


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

    seconds = parse_time_seconds_from_text(t)
    if seconds is not None:
        rec["time"] = seconds
        return

    txt = parse_time_text(t)
    if not txt:
        rec["time"] = None
        return

    rec["time"] = txt


def normalize_date_value(rec: dict[str, Any]) -> None:
    """Zamienia date dict na wartość "YYYY-MM-DD" lub "YYYY-MM" lub "YYYY"."""
    d = rec.get("date")
    if not isinstance(d, dict):
        return
    iso = d.get("iso")
    if isinstance(iso, list):
        rec["date"] = iso[0] if iso else None
        return
    if iso:
        rec["date"] = iso
        return

    txt = d.get("text")
    rec["date"] = txt.strip() if isinstance(txt, str) and txt.strip() else None
