from dataclasses import asdict, is_dataclass
from typing import Any, Mapping


def _normalize_value(value: Any) -> Any:
    if value is None:
        return None
    if hasattr(value, "to_dict") and callable(value.to_dict):
        return _normalize_value(value.to_dict())
    if isinstance(value, Mapping):
        return {key: _normalize_value(val) for key, val in value.items()}
    if hasattr(value, "model_dump") and callable(value.model_dump):
        return _normalize_value(value.model_dump())
    if hasattr(value, "dict") and callable(value.dict):
        return _normalize_value(value.dict())
    if is_dataclass(value):
        return _normalize_value(asdict(value))
    if isinstance(value, list):
        return [_normalize_value(item) for item in value]
    if isinstance(value, tuple):
        return [_normalize_value(item) for item in value]
    return value


def to_dict(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if hasattr(value, "to_dict") and callable(value.to_dict):
        return _normalize_value(value.to_dict())
    if isinstance(value, Mapping):
        return {key: _normalize_value(val) for key, val in value.items()}
    if hasattr(value, "model_dump"):
        return _normalize_value(value.model_dump())
    if hasattr(value, "dict"):
        return _normalize_value(value.dict())
    if is_dataclass(value):
        return _normalize_value(asdict(value))
    raise TypeError(f"Nieobsługiwany typ modelu: {type(value)!r}")


def to_dict_list(values: list[Any]) -> list[dict[str, Any]]:
    return [to_dict(value) for value in values]
