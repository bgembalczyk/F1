from dataclasses import asdict
from dataclasses import is_dataclass
from typing import Any

from models.domain_utils.normalization import (
    normalize_season_items as core_normalize_season_items,
)
from models.value_objects.link import Link
from models.value_objects.link_utils import validate_link as _validate_link
from models.value_objects.season_ref import SeasonRef


def normalize_season_list(
    items: list[SeasonRef | dict[str, Any] | None] | None,
) -> list[SeasonRef]:
    return list(core_normalize_season_items(items))


def model_to_dict(model: Any) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    if hasattr(model, "dict"):
        return model.dict()
    if is_dataclass(model):
        return asdict(model)
    msg = f"Nieobsługiwany typ modelu: {type(model)!r}"
    raise TypeError(msg)


def normalize_link_list(items: list[dict[str, Any] | Link] | None) -> list[Link]:
    normalized: list[Link] = []
    for item in items or []:
        raw = item.to_dict() if isinstance(item, Link) else item
        link = _validate_link(raw, field_name="links")
        if not link.get("text") and not link.get("url"):
            continue
        normalized.append(Link.from_dict(link))
    return normalized


def validate_links(
    items: list[dict[str, Any] | Link] | None,
    *,
    field_name: str,
) -> list[dict[str, Any]]:
    return [item.to_dict() for item in normalize_link_list(items)]


def validate_link(
    value: dict[str, Any] | Link | None,
    *,
    field_name: str,
) -> dict[str, Any]:
    payload = value.to_dict() if isinstance(value, Link) else value
    return _validate_link(payload, field_name=field_name)


def validate_seasons(
    items: list[SeasonRef | dict[str, Any] | None] | None,
) -> list[dict[str, Any]]:
    return [season.to_dict() for season in normalize_season_list(items)]
