from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

from models.value_objects.base import ValueObject


def normalize_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, ValueObject):
        return normalize_value(value.to_dict())
    if isinstance(value, Mapping):
        return {key: normalize_value(val) for key, val in value.items()}
    if hasattr(value, "model_dump") and callable(value.model_dump):
        return normalize_value(value.model_dump())
    if hasattr(value, "dict") and callable(value.dict):
        return normalize_value(value.dict())
    if is_dataclass(value):
        return normalize_value(asdict(value))
    if isinstance(value, list):
        return [normalize_value(item) for item in value]
    if isinstance(value, tuple):
        return [normalize_value(item) for item in value]
    return value


def to_dict(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, ValueObject):
        return normalize_value(value.to_dict())
    if isinstance(value, Mapping):
        return {key: normalize_value(val) for key, val in value.items()}
    if hasattr(value, "model_dump"):
        return normalize_value(value.model_dump())
    if hasattr(value, "dict"):
        return normalize_value(value.dict())
    if is_dataclass(value):
        return normalize_value(asdict(value))
    raise TypeError(f"Nieobsługiwany typ modelu: {type(value)!r}")


def to_dict_list(values: list[Any]) -> list[dict[str, Any]]:
    return [to_dict(value) for value in values]
