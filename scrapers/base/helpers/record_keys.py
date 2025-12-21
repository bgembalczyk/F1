"""Funkcje do ekstrakcji roku z rekordów i tworzenia kluczy identyfikacyjnych."""

from __future__ import annotations
from typing import Any
import re

from scrapers.base.helpers.text_processing import safe_text
from scrapers.base.helpers.time_processing import time_seconds

_YEAR_RE = re.compile(r"\b(1[89]\d{2}|20\d{2})\b")


def extract_year_from_event(rec: dict[str, Any]) -> str | None:
    """
    Fallback dla rekordów tabelarycznych, które nie mają `year` ani `date`,
    ale mają `event` (np. "1963 Aintree 200", url: ".../1963_Aintree_200").
    """
    event = rec.get("event")
    candidates: list[str] = []

    if isinstance(event, dict):
        if event.get("text"):
            candidates.append(str(event["text"]))
        if event.get("url"):
            candidates.append(str(event["url"]))
    elif isinstance(event, str):
        candidates.append(event)

    for s in candidates:
        m = _YEAR_RE.search(s)
        if m:
            return m.group(1)

    return None

def record_key(rec: dict[str, Any]) -> tuple | None:
    """
    Klucz do rozpoznawania tego samego rekordu:

    (driver_text, vehicle_text, year, time_seconds)

    - driver: rec["driver"]["text"] / rec["driver"]
    - vehicle: rec["vehicle"]["text"] / rec["car"]["text"]
    - year: rec["year"] albo rok z rec["date"]["iso"]
    - time: seconds lub sparsowany MM:SS.xxx

    UWAGA: series/category/class NIE jest częścią klucza – jeśli
    wszystko powyższe się zgadza, a różni się tylko series/category,
    traktujemy rekordy jako ten sam lap record.
    """
    driver_txt = safe_text(rec.get("driver"))

    vehicle_obj = rec.get("vehicle") or rec.get("car")
    vehicle_txt = safe_text(vehicle_obj)

    # year: najpierw pole year, potem date.iso, potem event
    year: str | None = None
    if rec.get("year") is not None:
        year = str(rec["year"])
    else:
        date_obj = rec.get("date")
        if isinstance(date_obj, dict):
            iso = (date_obj.get("iso") or "").strip()
            if iso:
                year = iso[:4]

    if not year:
        year = extract_year_from_event(rec)

    time_sec = time_seconds(rec)

    if not driver_txt or not vehicle_txt or not year or time_sec is None:
        return None

    # round dla stabilności klucza (minimalne różnice floatów)
    return (driver_txt, vehicle_txt, year, round(time_sec, 6))

def core_key(rec: dict[str, Any]) -> tuple | None:
    """
    Klucz „rdzeniowy" do łączenia rekordów nawet jeśli brakuje time.

    (driver_text, vehicle_text, year)

    - vehicle może być ucięty → dopasujemy fallbackiem prefiksowym w merge
    """
    driver_txt = safe_text(rec.get("driver"))
    vehicle_obj = rec.get("vehicle") or rec.get("car")
    vehicle_txt = safe_text(vehicle_obj)

    year: str | None = None
    if rec.get("year") is not None:
        year = str(rec["year"])
    else:
        date_obj = rec.get("date")
        if isinstance(date_obj, dict):
            iso = (date_obj.get("iso") or "").strip()
            if iso:
                year = iso[:4]

    if not year:
        year = extract_year_from_event(rec)

    if not driver_txt or not vehicle_txt or not year:
        return None

    return (driver_txt, vehicle_txt, year)
