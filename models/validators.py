from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, Dict, Iterable, Optional

from models.value_objects import Link, SeasonRef

def _coerce_number(value: Any, type_: type, field_name: str):
    if value is None:
        return None
    try:
        number = type_(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} musi być liczbą") from None
    if number < 0:
        raise ValueError(f"{field_name} nie może być ujemne")
    return number


def validate_int(value: Any, field_name: str) -> Optional[int]:
    return _coerce_number(value, int, field_name)


def validate_float(value: Any, field_name: str) -> Optional[float]:
    return _coerce_number(value, float, field_name)


def validate_link(link: Dict[str, Any] | None, *, field_name: str) -> Dict[str, Any]:
    if isinstance(link, Link):
        return link.to_dict()
    try:
        parsed = Link.from_dict(link)
    except ValueError as exc:
        raise ValueError(f"Pole {field_name} zawiera nieprawidłowy URL") from exc
    return parsed.to_dict()


def validate_links(
    links: Iterable[Dict[str, Any]] | None, *, field_name: str
) -> list[Dict[str, Any]]:
    result: list[Dict[str, Any]] = []
    for link in links or []:
        validated = validate_link(link, field_name=field_name)
        if validated["text"] or validated["url"] is not None:
            result.append(validated)
    return result


def validate_seasons(seasons: Iterable[Dict[str, Any]] | None) -> list[Dict[str, Any]]:
    result: list[Dict[str, Any]] = []
    for item in seasons or []:
        if isinstance(item, SeasonRef):
            season = item
        else:
            season = SeasonRef.from_dict(item)
        if season is None:
            continue
        result.append(season.to_dict())
    return result


def validate_status(value: Any, allowed: Iterable[str], field_name: str) -> str:
    status_normalized = (value or "").strip().lower()
    allowed_normalized: list[str] = []
    allowed_set: set[str] = set()
    for option in allowed:
        normalized = str(option).strip().lower()
        if normalized and normalized not in allowed_set:
            allowed_set.add(normalized)
            allowed_normalized.append(normalized)
    if status_normalized not in allowed_set:
        allowed_display = ", ".join(allowed_normalized)
        raise ValueError(
            f"Pole {field_name} musi mieć jedną z wartości: {allowed_display}"
        )
    return status_normalized


def model_to_dict(model: Any) -> Dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    if hasattr(model, "dict"):
        return model.dict()
    if is_dataclass(model):
        return asdict(model)
    raise TypeError("Nieobsługiwany typ modelu")
