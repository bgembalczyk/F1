from typing import Any
from typing import Mapping

from models.domain_utils.normalization import (
    normalize_link_items as core_normalize_link_items,
    normalize_season_items as core_normalize_season_items,
)
from models.mappers.serialization import to_dict as model_to_dict
from models.value_objects.link import Link
from models.value_objects.link_utils import validate_link
from models.value_objects.season_ref import SeasonRef


def normalize_season_list(
    items: list[SeasonRef | dict[str, Any] | None] | None,
) -> list[SeasonRef]:
    return list(core_normalize_season_items(items))


def normalize_link_list(
    items: list[Link | Mapping[str, Any] | str | None] | None,
) -> list[Link]:
    normalized = core_normalize_link_items(items, field_name="links")
    return [Link.from_dict(item) for item in normalized]


def validate_links(
    items: list[Link | Mapping[str, Any] | str | None] | None,
    *,
    field_name: str = "links",
) -> list[dict[str, Any]]:
    return core_normalize_link_items(items, field_name=field_name)


def validate_seasons(
    items: list[SeasonRef | Mapping[str, Any] | None] | None,
) -> list[dict[str, Any]]:
    return [season.to_dict() for season in core_normalize_season_items(items)]
