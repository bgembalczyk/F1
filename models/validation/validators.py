import logging
from collections.abc import Iterable
from typing import Any

from models.domain_utils.normalization import (
    normalize_link_item as core_normalize_link_item,
)
from models.domain_utils.normalization import (
    normalize_link_items as core_normalize_link_items,
)
from models.domain_utils.normalization import (
    normalize_season_item as core_normalize_season_item,
)
from models.domain_utils.normalization import (
    normalize_season_items as core_normalize_season_items,
)
from models.serializers import to_dict_any
from models.value_objects.link import Link
from models.value_objects.season_ref import SeasonRef


def validate_link(
    link: dict[str, Any] | Link | None,
    *,
    field_name: str,
) -> dict[str, Any] | None:
    return core_normalize_link_item(link, field_name=field_name)


def validate_links(
    links: Iterable[dict[str, Any] | Link | None] | None,
    *,
    field_name: str,
) -> list[dict[str, Any]]:
    return core_normalize_link_items(links, field_name=field_name)


def normalize_season_item(
    item: dict[str, Any] | SeasonRef | None,
) -> dict[str, Any] | None:
    season = core_normalize_season_item(item)
    return season.to_dict() if season is not None else None


def validate_seasons(
    seasons: Iterable[dict[str, Any] | SeasonRef | None] | None,
) -> list[dict[str, Any]]:
    return [season.to_dict() for season in core_normalize_season_items(seasons)]


def model_to_dict(
    model: Any,
    *,
    logger: logging.Logger | logging.LoggerAdapter | None = None,
) -> dict[str, Any]:
    result = to_dict_any(model, logger=logger)
    if not isinstance(result, dict):
        msg = "Nieobsługiwany typ modelu"
        raise TypeError(msg)
    return result


def normalize_link_list(
    items: list[Link | dict[str, Any] | None] | None,
) -> list[Link]:
    return [
        Link.from_dict(item)
        for item in core_normalize_link_items(items, field_name="link")
    ]


def normalize_season_list(
    items: list[SeasonRef | dict[str, Any] | None] | None,
) -> list[SeasonRef]:
    return list(core_normalize_season_items(items))


def filter_nonempty(items: Iterable[Any] | None, *, key: Any = None) -> list[Any]:
    result: list[Any] = []
    for item in items or []:
        if item is None:
            continue
        if key is not None and key(item):
            continue
        result.append(item)
    return result
