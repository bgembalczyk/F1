from dataclasses import asdict, is_dataclass
from typing import Any, Mapping


def to_dict(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if hasattr(value, "to_dict") and callable(value.to_dict):
        return value.to_dict()
    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "dict"):
        return value.dict()
    if is_dataclass(value):
        return asdict(value)
    raise TypeError(f"Nieobsługiwany typ modelu: {type(value)!r}")


def to_dict_list(values: list[Any]) -> list[dict[str, Any]]:
    return [to_dict(value) for value in values]
