from collections.abc import Callable
from collections.abc import Mapping
from dataclasses import asdict
from dataclasses import is_dataclass
from typing import Any
from typing import Protocol
from typing import runtime_checkable

from models.records.circuit_base import CircuitBaseRecord
from models.records.circuit_complete import CircuitCompleteRecord
from models.records.circuit_details import CircuitDetailsRecord
from models.value_objects.base import ValueObject


@runtime_checkable
class SerializableProtocol(Protocol):
    def to_serializable(self) -> Any: ...


SerializableAdapter = Callable[[Any], Any]

_SERIALIZABLE_ADAPTERS: dict[type[Any], SerializableAdapter] = {}


def register_serializable_adapter(
    model_type: type[Any],
    adapter: SerializableAdapter,
) -> None:
    _SERIALIZABLE_ADAPTERS[model_type] = adapter


def clear_serializable_adapters() -> None:
    _SERIALIZABLE_ADAPTERS.clear()


def _extract_registered_adapter(value: Any) -> Any | None:
    for model_type, adapter in _SERIALIZABLE_ADAPTERS.items():
        if isinstance(value, model_type):
            return adapter(value)
    return None


def _extract_serializable(value: Any) -> Any:
    if isinstance(value, ValueObject):
        return value.to_dict()
    if isinstance(value, SerializableProtocol):
        return value.to_serializable()

    adapted = _extract_registered_adapter(value)
    if adapted is not None:
        return adapted

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


def to_dict(value: Any) -> dict[str, Any]:
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
    | Mapping[str, Any],
) -> dict[str, Any]:
    return to_dict(value)


def to_dict_list(values: list[Any]) -> list[dict[str, Any]]:
    return [to_dict(value) for value in values]
