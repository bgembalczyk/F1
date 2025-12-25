import logging
from dataclasses import asdict, is_dataclass
from typing import Any, Mapping, cast

from models.records.link import LinkRecord

Primitive = str | int | float | bool | None


def to_dict_any(
    value: Any,
    *,
    logger: logging.Logger | logging.LoggerAdapter | None = None,
) -> dict[str, Any] | list[Any] | Primitive:
    if hasattr(value, "to_dict") and callable(value.to_dict):
        return to_dict_any(value.to_dict(), logger=logger)
    if hasattr(value, "model_dump") and callable(value.model_dump):
        return to_dict_any(value.model_dump(), logger=logger)
    if hasattr(value, "dict") and callable(value.dict):
        return to_dict_any(value.dict(), logger=logger)
    if is_dataclass(value):
        return to_dict_any(asdict(value), logger=logger)
    if isinstance(value, Mapping):
        if (
            "text" in value
            and "url" in value
            and set(value.keys()).issubset({"text", "url"})
        ):
            return cast(
                LinkRecord,
                {"text": value.get("text") or "", "url": value.get("url")},
            )
        return {k: to_dict_any(v, logger=logger) for k, v in value.items()}
    if isinstance(value, list):
        return [to_dict_any(v, logger=logger) for v in value]
    if isinstance(value, tuple):
        return [to_dict_any(v, logger=logger) for v in value]
    if isinstance(value, (str, int, float, bool, type(None))):
        return value
    if logger is not None:
        logger.debug("Nieobsługiwany typ: %s", type(value).__name__)
    return value
