from __future__ import annotations

from dataclasses import asdict
from dataclasses import is_dataclass
from typing import Any

from models.domain_utils.normalization import normalize_link_items
from models.domain_utils.normalization import normalize_season_items as core_normalize_season_items
from models.value_objects.link import Link
from models.value_objects.link_utils import validate_link as validate_link_payload
from models.value_objects.season_ref import SeasonRef


def model_to_dict(model: Any) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return dict(model.model_dump())
    if hasattr(model, "dict"):
        return dict(model.dict())
    if is_dataclass(model):
        return asdict(model)
    msg = "Nieobsługiwany typ modelu"
    raise TypeError(msg)


def validate_link(value: Any, *, field_name: str) -> dict[str, Any]:
    if isinstance(value, Link):
        payload = value.to_dict()
    elif isinstance(value, dict) or value is None:
        payload = value
    else:
        msg = f"Pole {field_name} musi być linkiem"
        raise ValueError(msg)
    return validate_link_payload(payload, field_name=field_name)


def validate_links(values: list[Any] | None, *, field_name: str) -> list[dict[str, Any]]:
    if values is None:
        return []
    normalized: list[dict[str, Any]] = []
    for index, value in enumerate(values):
        item = validate_link(value, field_name=f"{field_name}[{index}]")
        if item.get("text") or item.get("url"):
            normalized.append(item)
    return normalized


def normalize_link_list(items: list[Link | dict[str, Any] | None] | None) -> list[Link]:
    normalized = normalize_link_items(items, field_name="links")
    return [Link.from_dict(item) for item in normalized if Link.from_dict(item) is not None]


def normalize_season_list(
    items: list[SeasonRef | dict[str, Any] | None] | None,
) -> list[SeasonRef]:
    return list(core_normalize_season_items(items))


def validate_seasons(
    items: list[SeasonRef | dict[str, Any] | None] | None,
) -> list[dict[str, Any]]:
    seasons = normalize_season_list(items)
    return [season.to_dict() for season in seasons]
