from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, Dict, Iterable, Optional
from urllib.parse import urlparse


def _coerce_number(value: Any, type_: type, field_name: str):
    if value is None:
        return None
    try:
        number = type_(value)
    except (TypeError, ValueError):
        raise ValueError(f"Pole {field_name} musi być liczbą") from None
    if number < 0:
        raise ValueError(f"Pole {field_name} nie może być ujemne")
    return number


def validate_int(value: Any, field_name: str) -> Optional[int]:
    return _coerce_number(value, int, field_name)


def validate_float(value: Any, field_name: str) -> Optional[float]:
    return _coerce_number(value, float, field_name)


def _is_valid_url(url: str) -> bool:
    parsed = urlparse(url)
    return bool(parsed.scheme in {"http", "https"} and parsed.netloc)


def validate_link(link: Dict[str, Any] | None, *, field_name: str) -> Dict[str, Any]:
    link = link or {}
    text = str(link.get("text") or "").strip()
    url = link.get("url")

    if url:
        if not isinstance(url, str) or not _is_valid_url(url):
            raise ValueError(f"Pole {field_name} zawiera nieprawidłowy URL")

    return {"text": text, "url": url}


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
        year = item.get("year")
        url = item.get("url")
        if year is None:
            continue
        year_int = validate_int(year, "year")
        if year_int is None:
            continue
        validated = {"year": year_int}
        if url:
            if not _is_valid_url(url):
            raise ValueError("Pole seasons zawiera nieprawidłowy URL")
            validated["url"] = url
        result.append(validated)
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
