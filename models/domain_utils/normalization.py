from collections.abc import Iterable
from collections.abc import Mapping
from typing import Any

from models.records.constants import WIKI_SEASON_URL
from models.value_objects.season_ref import SeasonRef


def normalize_season_item(
    value: SeasonRef | Mapping[str, Any] | None,
    *,
    with_default_url: bool = False,
) -> SeasonRef | None:
    """Normalize a single season item.

    Contract:
    - empty payload -> None,
    - invalid payload -> ValueError,
    - valid payload -> SeasonRef.
    """
    if value is None:
        return None

    if isinstance(value, SeasonRef):
        season = value
    elif isinstance(value, Mapping) or value is None:
        season = SeasonRef.from_dict(value)
    else:
        msg = "Pole seasons musi być obiektem SeasonRef albo słownikiem"
        raise ValueError(msg)
    if season is None:
        return None

    if with_default_url and season.url is None:
        return SeasonRef(year=season.year, url=WIKI_SEASON_URL.format(year=season.year))
    return season


def normalize_season_items(
    values: Iterable[SeasonRef | Mapping[str, Any] | None] | None,
    *,
    with_default_url: bool = False,
) -> list[SeasonRef]:
    if values is None:
        return []

    normalized: list[SeasonRef] = []
    for value in values:
        item = normalize_season_item(value, with_default_url=with_default_url)
        if item is not None:
            normalized.append(item)
    return normalized
