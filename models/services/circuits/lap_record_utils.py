"""Wspólne narzędzia do obsługi rekordów lap record."""

from __future__ import annotations

from typing import Any, Callable, Iterable, Mapping

from scrapers.base.helpers.text import normalize_text
from scrapers.base.helpers.time import parse_time_seconds, parse_time_seconds_from_text


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


def normalize_lap_record_driver(
    value: Any, *, sanitizer: Callable[[str], str] | None = None
) -> str:
    """Normalizuje tekst kierowcy."""
    return normalize_lap_record_entity(value, sanitizer=sanitizer)


def normalize_lap_record_vehicle(
    value: Any, *, sanitizer: Callable[[str], str] | None = None
) -> str:
    """Normalizuje tekst pojazdu."""
    return normalize_lap_record_entity(value, sanitizer=sanitizer)


def parse_lap_record_time(value: Any) -> float | None:
    """Parsuje wartość czasu na sekundy (float)."""
    return parse_time_seconds_from_text(value)


def parse_lap_record_time_from_record(rec: Mapping[str, Any]) -> float | None:
    """Parsuje czas z rekordu (obsługa time_seconds/time)."""
    return parse_time_seconds(rec)


def choose_richer_entity(a: Any, b: Any) -> Any:
    """
    Preferuj encję z url; jeśli oba mają url albo oba nie mają,
    wybierz tę z dłuższym textem.
    """
    if not a:
        return b
    if not b:
        return a

    if isinstance(a, dict) and not isinstance(b, dict):
        return a
    if isinstance(b, dict) and not isinstance(a, dict):
        return b

    a_url = a.get("url") if isinstance(a, dict) else None
    b_url = b.get("url") if isinstance(b, dict) else None
    if a_url and not b_url:
        return a
    if b_url and not a_url:
        return b

    a_txt = (a.get("text") if isinstance(a, dict) else str(a or "")).strip()
    b_txt = (b.get("text") if isinstance(b, dict) else str(b or "")).strip()
    return a if len(a_txt) >= len(b_txt) else b


def select_best_field_with_url(
    records: Iterable[Mapping[str, Any]], *field_names: str
) -> Any:
    """Wybiera najlepszą wartość pola (preferuje dict z URL)."""
    best = None
    for r in records:
        value = None
        for field_name in field_names:
            value = r.get(field_name)
            if value is not None:
                break

        if not value:
            continue
        if best is None:
            best = value
            continue
        if (
            isinstance(value, dict)
            and value.get("url")
            and (not isinstance(best, dict) or not best.get("url"))
        ):
            best = value
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
        else normalize_lap_record_driver(driver_value)
    )
    vehicle_norm = (
        vehicle_normalizer(vehicle_value)
        if vehicle_normalizer is not None
        else normalize_lap_record_vehicle(vehicle_value)
    )

    time_value = (
        time_extractor(rec)
        if time_extractor is not None
        else parse_lap_record_time_from_record(rec)
    )
    year_value = (
        year_extractor(rec) if year_extractor is not None else rec.get("year")
    )
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
