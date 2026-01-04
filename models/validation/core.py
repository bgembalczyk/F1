from typing import Any, Iterable, Optional

from models.validation.utils import coerce_number


def validate_int(value: Any, field_name: str) -> Optional[int]:
    return coerce_number(value, int, field_name, allow_none=True)


def validate_float(value: Any, field_name: str) -> Optional[float]:
    return coerce_number(value, float, field_name, allow_none=True)


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
