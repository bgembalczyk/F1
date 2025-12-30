from typing import Any
from typing import Dict
from typing import List

from models.validation.validators import validate_float


def normalize_unit_value(value: Any, field_name: str) -> Dict[str, Any] | None:
    if value is None:
        return None
    if isinstance(value, dict):
        raw_value = value.get("value")
        unit = value.get("unit")
        normalized_value = (
            validate_float(raw_value, f"{field_name}.value")
            if raw_value is not None
            else None
        )
        normalized_unit = str(unit).strip() if unit is not None else None
        return {"value": normalized_value, "unit": normalized_unit}
    if isinstance(value, (int, float)):
        return {"value": validate_float(value, f"{field_name}.value"), "unit": None}
    raise ValueError(f"Pole {field_name} musi być słownikiem lub liczbą")


def normalize_unit_list(value: Any, field_name: str) -> List[Dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"Pole {field_name} musi być listą")
    normalized: List[Dict[str, Any]] = []
    for index, item in enumerate(value):
        normalized_item = normalize_unit_value(item, f"{field_name}[{index}]")
        if normalized_item is not None:
            normalized.append(normalized_item)
    return normalized


def normalize_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def normalize_range_value(value: Any, field_name: str) -> Dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise ValueError(f"Pole {field_name} musi być słownikiem")

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
    if isinstance(value, (int, float, dict)):
        return normalize_unit_value(value, field_name)
    raise ValueError(f"Pole {field_name} ma nieprawidłowy typ")
