from __future__ import annotations

from typing import TYPE_CHECKING
from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Mapping
from typing import Any

if TYPE_CHECKING:
    from models.records.link import LinkRecord



def normalize_link_payload(link: Mapping[str, Any] | None) -> dict[str, Any]:
    data: dict[str, Any] = dict(link or {})
    text = str(data.get("text") or "").strip()
    url = data.get("url")
    if url == "":
        url = None
    return {"text": text, "url": url}


def _is_link_object(value: Any) -> bool:
    return (
        hasattr(value, "to_dict") and hasattr(value, "text") and hasattr(value, "url")
    )


def is_empty_link(value: Any) -> bool:
    if value is None:
        return True

    if _is_link_object(value):
        text = str(getattr(value, "text", "") or "").strip()
        url = getattr(value, "url", None)
    elif isinstance(value, Mapping):
        normalized = normalize_link_payload(value)
        text = normalized["text"]
        url = normalized["url"]
    else:
        return False

    return text == "" and url is None


def normalize_link_item(
    value: Any,
    *,
    field_name: str,
    validate_payload: Callable[..., dict[str, Any]],
) -> LinkRecord | None:
    if isinstance(value, str):
        text = value.strip()
        normalized = {"text": text, "url": None} if text else None
    elif _is_link_object(value):
        normalized = value.to_dict()
    elif isinstance(value, Mapping) or value is None:
        normalized = validate_payload(value, field_name=field_name)
    else:
        msg = f"Pole {field_name} musi być linkiem, słownikiem lub tekstem"
        raise ValueError(msg)

    if normalized is None:
        return None
    return None if is_empty_link(normalized) else normalized


def normalize_link_items(
    values: Iterable[Any] | None,
    *,
    field_name: str,
    validate_payload: Callable[..., dict[str, Any]],
) -> list[LinkRecord]:
    if values is None:
        return []

    normalized: list[LinkRecord] = []
    for value in values:
        item = normalize_link_item(
            value,
            field_name=field_name,
            validate_payload=validate_payload,
        )
        if item is not None:
            normalized.append(item)
    return normalized
