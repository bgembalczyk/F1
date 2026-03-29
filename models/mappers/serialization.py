from collections.abc import Mapping
from dataclasses import asdict
from dataclasses import is_dataclass
from typing import Any
from typing import TypeAlias

from models.records.circuit_base import CircuitBaseRecord
from models.records.circuit_complete import CircuitCompleteRecord
from models.records.circuit_details import CircuitDetailsRecord
from models.value_objects.base import ValueObject

JSONScalar: TypeAlias = str | int | float | bool | None
JSONValue: TypeAlias = JSONScalar | list["JSONValue"] | dict[str, "JSONValue"]
QualityRecord: TypeAlias = Mapping[str, JSONValue]


def _extract_serializable(value: Any) -> Any:
    if isinstance(value, ValueObject):
        return value.to_dict()
    if hasattr(value, "model_dump") and callable(value.model_dump):
        return value.model_dump()
    if hasattr(value, "dict") and callable(value.dict):
        return value.dict()
    if is_dataclass(value):
        return asdict(value)
    return value


def normalize_value(value: Any) -> Any:
    value = _extract_serializable(value)

    if value is None:
        return None
    if isinstance(value, Mapping):
        return {key: normalize_value(val) for key, val in value.items()}
    if isinstance(value, list):
        return [normalize_value(item) for item in value]
    if isinstance(value, tuple):
        return [normalize_value(item) for item in value]
    return value


def to_dict(value: object) -> dict[str, JSONValue]:
    if value is None:
        return {}

    normalized = normalize_value(_extract_serializable(value))
    if isinstance(normalized, Mapping):
        return dict(normalized)

    msg = f"Nieobsługiwany typ modelu: {type(value)!r}"
    raise TypeError(msg)


def to_circuit_record_dict(
    value: CircuitBaseRecord
    | CircuitCompleteRecord
    | CircuitDetailsRecord
    | Mapping[str, JSONValue],
) -> dict[str, JSONValue]:
    return to_dict(value)


def to_dict_list(values: list[object]) -> list[dict[str, JSONValue]]:
    return [to_dict(value) for value in values]
