"""Wspólne narzędzia do obsługi rekordów lap record."""

import re
from typing import Any, Callable, Iterable, Mapping

from models.value_objects.normalized_date import NormalizedDate
from scrapers.base.helpers.text import choose_richer_entity
from scrapers.base.helpers.text_normalization import normalize_text
from scrapers.base.helpers.time import parse_time_seconds_from_text


def extract_year_from_event(rec: dict[str, Any]) -> str | None:
    """
    Fallback do ekstrakcji roku z pola event (np. "1963 Aintree 200").
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

    year_re = re.compile(r"\b(1[89]\d{2}|20\d{2})\b")
    for s in candidates:
        m = year_re.search(s)
        if m:
            return m.group(1)

    return None


def extract_year(rec: dict[str, Any]) -> str | None:
    """
    Wspólna logika ekstrakcji roku z rekordu.
    Próbuje kolejno: year, date (iso), event.
    """
    if rec.get("year") is not None:
        return str(rec["year"])

    date_obj = rec.get("date")
    if isinstance(date_obj, dict):
        iso = (date_obj.get("iso") or "").strip()
        if iso:
            return iso[:4]
    if isinstance(date_obj, NormalizedDate):
        iso = (date_obj.iso or "").strip()
        if iso:
            return iso[:4]

    return extract_year_from_event(rec)


def normalize_lap_record_entity(
    value: Any, *, sanitizer: Callable[[str], str] | None = None
) -> str:
    """Normalizuje tekst encji (driver/vehicle) z opcjonalnym czyszczeniem."""
    text = normalize_text(value)
    if not text:
        return ""
    if sanitizer:
        text = sanitizer(text)
        text = normalize_text(text)
    return text


def parse_lap_record_time_from_record(rec: Mapping[str, Any]) -> float | None:
    """
    Parsuje czas z rekordu (obsługa time_seconds/time).
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


def has_meaningful_value(candidate: Any) -> bool:
    if candidate is None:
        return False
    if isinstance(candidate, dict):
        text = (candidate.get("text") or candidate.get("name") or "").strip()
        url = candidate.get("url")
        return bool(text or url)
    if isinstance(candidate, str):
        return bool(candidate.strip())
    return True


def select_best_field_with_url(
    records: Iterable[Mapping[str, Any]], *field_names: str
) -> Any:
    """Wybiera najlepszą wartość pola (preferuje bogatszą encję)."""
    best = None
    for r in records:
        value = None
        for field_name in field_names:
            candidate = r.get(field_name)
            if has_meaningful_value(candidate):
                value = candidate
                break

        if value is None:
            continue
        best = choose_richer_entity(best, value)
    return best


def build_lap_record_key(
    rec: Mapping[str, Any],
    *,
    year_extractor: Callable[[Mapping[str, Any]], str | None] | None = None,
    vehicle_getter: Callable[[Mapping[str, Any]], Any] | None = None,
    time_extractor: Callable[[Mapping[str, Any]], float | None] | None = None,
    driver_normalizer: Callable[[Any], str] | None = None,
    vehicle_normalizer: Callable[[Any], str] | None = None,
    time_key_factory: Callable[[float], Any] | None = None,
    key_order: tuple[str, ...] = ("driver", "vehicle", "year", "time"),
) -> tuple | None:
    """Buduje klucz rekordu lap record z parametryzacją źródeł danych."""
    driver_value = rec.get("driver")
    vehicle_value = (
        vehicle_getter(rec)
        if vehicle_getter is not None
        else rec.get("vehicle") or rec.get("car")
    )
    driver_norm = (
        driver_normalizer(driver_value)
        if driver_normalizer is not None
        else normalize_lap_record_entity(driver_value)
    )
    vehicle_norm = (
        vehicle_normalizer(vehicle_value)
        if vehicle_normalizer is not None
        else normalize_lap_record_entity(vehicle_value)
    )

    time_value = (
        time_extractor(rec)
        if time_extractor is not None
        else parse_lap_record_time_from_record(rec)
    )
    year_value = year_extractor(rec) if year_extractor is not None else rec.get("year")
    year_norm = str(year_value).strip() if year_value is not None else ""

    if not driver_norm or not vehicle_norm or not year_norm or time_value is None:
        return None

    time_key = (
        time_key_factory(float(time_value))
        if time_key_factory is not None
        else round(float(time_value), 6)
    )

    parts = {
        "driver": driver_norm,
        "vehicle": vehicle_norm,
        "year": year_norm,
        "time": time_key,
    }

    return tuple(parts[name] for name in key_order)
