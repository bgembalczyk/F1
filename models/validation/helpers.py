from collections.abc import Iterable
from typing import Any

from models.validation.utils import coerce_number


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
        msg = f"Pole {field_name} musi mieć jedną z wartości: {allowed_display}"
        raise ValueError(msg)
    return status_normalized


def normalize_unit_value(value: Any, field_name: str) -> dict[str, Any] | None:
    if value is None:
        return None
    if isinstance(value, dict):
        raw_value = value.get("value")
        unit = value.get("unit")
        normalized_value = (
            coerce_number(raw_value, float, f"{field_name}.value", allow_none=True)
            if raw_value is not None
            else None
        )
        normalized_unit = str(unit).strip() if unit is not None else None
        return {"value": normalized_value, "unit": normalized_unit}
    if isinstance(value, int | float):
        return {
            "value": coerce_number(value, float, f"{field_name}.value", allow_none=True),
            "unit": None,
        }
    msg = f"Pole {field_name} musi być słownikiem lub liczbą"
    raise TypeError(msg)


def normalize_unit_list(value: Any, field_name: str) -> list[dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        msg = f"Pole {field_name} musi być listą"
        raise TypeError(msg)
    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        normalized_item = normalize_unit_value(item, f"{field_name}[{index}]")
        if normalized_item is not None:
            normalized.append(normalized_item)
    return normalized


def normalize_range_value(value: Any, field_name: str) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        msg = f"Pole {field_name} musi być słownikiem"
        raise TypeError(msg)

    lower = value.get("min")
    upper = value.get("max")

    return {
        "min": normalize_range_item(lower, f"{field_name}.min"),
        "max": normalize_range_item(upper, f"{field_name}.max"),
    }


def normalize_range_item(value: Any, field_name: str) -> Any:
    if value is None:
        return None
    if isinstance(value, dict) and "unit" in value:
        return normalize_unit_value(value, field_name)
    if isinstance(value, int | float | dict):
        return normalize_unit_value(value, field_name)
    msg = f"Pole {field_name} ma nieprawidłowy typ"
    raise ValueError(msg)
