from collections.abc import Iterable
from collections.abc import Mapping
from typing import Any

from models.records.constants import WIKI_SEASON_URL
from models.value_objects.link import Link
from models.value_objects.link_utils import validate_link as validate_link_payload
from models.value_objects.season_ref import SeasonRef


def normalize_link_item(
    value: Link | Mapping[str, Any] | str | None,
    *,
    field_name: str,
) -> dict[str, Any] | None:
    """Normalize a single link item.

    Contract:
    - empty payload -> None,
    - invalid payload -> ValueError,
    - valid payload -> {"text": str, "url": str | None}.
    """
    if isinstance(value, str):
        text = value.strip()
        return {"text": text, "url": None} if text else None

    if isinstance(value, Link):
        normalized = value.to_dict()
    elif isinstance(value, Mapping) or value is None:
        normalized = validate_link_payload(value, field_name=field_name)
    else:
        msg = f"Pole {field_name} musi być linkiem, słownikiem lub tekstem"
        raise ValueError(msg)

    return None if is_empty_link(normalized) else normalized


def normalize_link_items(
    values: Iterable[Link | Mapping[str, Any] | str | None] | None,
    *,
    field_name: str,
) -> list[dict[str, Any]]:
    if values is None:
        return []

    normalized: list[dict[str, Any]] = []
    for value in values:
        item = normalize_link_item(value, field_name=field_name)
        if item is not None:
            normalized.append(item)
    return normalized


def normalize_season_item(
    value: SeasonRef | Mapping[str, Any] | None,
    *,
    with_default_url: bool = False,
) -> dict[str, Any] | None:
    """Normalize a single season item.

    Contract:
    - empty payload -> None,
    - invalid payload -> ValueError,
    - valid payload -> {"year": int, "url": str?}.
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

    result = season.to_dict()
    if with_default_url and "url" not in result:
        result["url"] = WIKI_SEASON_URL.format(year=result["year"])
    return result


def normalize_season_items(
    values: Iterable[SeasonRef | Mapping[str, Any] | None] | None,
    *,
    with_default_url: bool = False,
) -> list[dict[str, Any]]:
    if values is None:
        return []

    normalized: list[dict[str, Any]] = []
    for value in values:
        item = normalize_season_item(value, with_default_url=with_default_url)
        if item is not None:
            normalized.append(item)
    return normalized


def is_empty_link(value: Link | Mapping[str, Any] | None) -> bool:
    if value is None:
        return True

    if isinstance(value, Link):
        text = value.text
        url = value.url
    else:
        text = str(value.get("text") or "").strip()
        url = value.get("url")
        if url == "":
            url = None

    return text == "" and url is None
