"""Time and date normalization helpers for record data."""

import re
from datetime import datetime
from datetime import timezone
from decimal import ROUND_HALF_UP
from decimal import Decimal
from typing import Any

from models.value_objects.time_types import DateValue
from scrapers.base.helpers.constants import DATE_FORMATS
from scrapers.base.helpers.constants import DATE_ISO_FULL_RE
from scrapers.base.helpers.constants import DATE_ISO_MONTH_RE
from scrapers.base.helpers.constants import DATE_ISO_YEAR_RE
from scrapers.base.helpers.constants import DATE_RANGE_SPLIT
from scrapers.base.helpers.constants import TIME_SECONDS_RE
from scrapers.base.helpers.constants import YEAR_RE
from scrapers.base.helpers.value_objects.normalized_time import NormalizedTime


def extract_time_value(value: Any) -> tuple[str | None, float | None]:
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
        sec = float(seconds) if isinstance(seconds, int | float) else None
        txt = str(text).strip() if text is not None else None
        return (txt or None), sec

    if isinstance(value, int | float):
        return None, float(value)

    if value is not None:
        return str(value), None

    return None, None


def seconds_from_match(match: re.Match[str]) -> float:
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
    txt, seconds = extract_time_value(value)
    if seconds is not None:
        return seconds

    if txt is None:
        return None

    s = str(txt).strip()
    if not s:
        return None

    match = TIME_SECONDS_RE.match(s)
    if not match:
        return None

    return seconds_from_match(match)


def parse_time_text(value: Any) -> str | None:
    txt, _ = extract_time_value(value)
    if txt is None:
        return None
    s = str(txt).strip()
    return s or None


def clean_date_base(text: str) -> str:
    base = text.split("(", 1)[0].strip()
    parts = DATE_RANGE_SPLIT.split(base)
    if len(parts) > 1:
        first = parts[0].strip()
        tail = parts[-1].strip()
        if any(ch.isalpha() for ch in tail):
            base = f"{first} {tail}"
        else:
            base = parts[0].strip()
    return base


def _parse_with_formats(base: str, formats: tuple[str, ...]) -> datetime | None:
    for fmt in formats:
        parsed = None
        try:
            parsed = datetime.strptime(base, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        if parsed is not None:
            return parsed
    return None


def parse_date_iso(base: str) -> str | None:
    parsed_date = _parse_with_formats(base, tuple(DATE_FORMATS))
    if parsed_date is not None:
        return parsed_date.date().isoformat()

    parsed_month = _parse_with_formats(base, ("%B %Y", "%b %Y"))
    if parsed_month is not None:
        return parsed_month.strftime("%Y-%m")

    if DATE_ISO_YEAR_RE.fullmatch(base):
        return base

    return None


def parse_date_parts(value: str) -> tuple[int | None, int | None, int | None]:
    if DATE_ISO_FULL_RE.fullmatch(value):
        year, month, day = value.split("-")
        return int(year), int(month), int(day)
    if DATE_ISO_MONTH_RE.fullmatch(value):
        year, month = value.split("-")
        return int(year), int(month), None
    if DATE_ISO_YEAR_RE.fullmatch(value):
        return int(value), None, None
    return None, None, None


def parse_date_text(text: str) -> DateValue:
    stripped = text.strip() if text else ""
    if not stripped:
        return DateValue(raw=None, iso=None, year=None, month=None, day=None)

    iso_full = DATE_ISO_FULL_RE.findall(stripped)
    iso_month = DATE_ISO_MONTH_RE.findall(stripped)
    years = YEAR_RE.findall(stripped)

    iso: str | list[str] | None = None
    if iso_full:
        iso = iso_full
    elif iso_month:
        iso = iso_month

    if iso is None:
        base = clean_date_base(stripped)
        iso = parse_date_iso(base)

    year = month = day = None
    if isinstance(iso, list):
        if iso:
            year, month, day = parse_date_parts(iso[0])
    elif isinstance(iso, str):
        year, month, day = parse_date_parts(iso)

    if year is None and years:
        year = int(years[0])

    return DateValue(
        raw=stripped or None,
        iso=iso,
        year=year,
        month=month,
        day=day,
    )


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
