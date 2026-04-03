import logging
from collections.abc import Mapping
from dataclasses import asdict
from dataclasses import is_dataclass
from typing import TYPE_CHECKING
from typing import Protocol
from typing import TypeVar
from typing import cast
from typing import runtime_checkable

from models.contracts.helpers import map_record_to_contract

if TYPE_CHECKING:
    from models.records.link import LinkRecord

Primitive = str | int | float | bool | None
SerializableValue = (
    Primitive | list["SerializableValue"] | dict[str, "SerializableValue"]
)
SerializerInputT_contra = TypeVar("SerializerInputT_contra", contravariant=True)
SerializerOutputT_co = TypeVar("SerializerOutputT_co", covariant=True)


@runtime_checkable
class SerializerProtocol(Protocol[SerializerInputT_contra, SerializerOutputT_co]):
    """Public serializer contract used by mappers and export adapters."""

    def serialize(self, value: SerializerInputT_contra) -> SerializerOutputT_co: ...


def _extract_supported_mapping(value: object) -> Mapping[str, object] | None:
    for attr_name in ("to_dict", "model_dump", "dict"):
        attr = getattr(value, attr_name, None)
        if callable(attr):
            extracted = attr()
            if isinstance(extracted, Mapping):
                return extracted
            return None
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, Mapping):
        return value
    return None


def _normalize_link_mapping(value: Mapping[str, object]) -> dict[str, object] | None:
    if "text" not in value or "url" not in value:
        return None
    if not set(value.keys()).issubset({"text", "url"}):
        return None
    return cast(
        "LinkRecord",
        {"text": value.get("text") or "", "url": value.get("url")},
    )


def to_dict_any(
    value: object,
    *,
    logger: logging.Logger | logging.LoggerAdapter | None = None,
) -> SerializableValue:
    mapping = _extract_supported_mapping(value)
    if mapping is not None:
        normalized_link = _normalize_link_mapping(mapping)
        if normalized_link is not None:
            return normalized_link
        mapped = map_record_to_contract(mapping)
        return {k: to_dict_any(v, logger=logger) for k, v in mapped.items()}

    if isinstance(value, list | tuple):
        return [to_dict_any(v, logger=logger) for v in value]

    if isinstance(value, str | int | float | bool | type(None)):
        return value

    if logger is not None:
        logger.debug("Nieobsługiwany typ: %s", type(value).__name__)
    return value
