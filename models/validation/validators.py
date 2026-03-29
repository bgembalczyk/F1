from typing import Any

from models.domain_utils.normalization import (
    normalize_season_items as core_normalize_season_items,
)
from models.value_objects.season_ref import SeasonRef


def normalize_season_list(
    items: list[SeasonRef | dict[str, Any] | None] | None,
) -> list[SeasonRef]:
    return list(core_normalize_season_items(items))
