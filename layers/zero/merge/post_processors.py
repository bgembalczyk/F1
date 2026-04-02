from __future__ import annotations

import json
from collections.abc import Callable

from scrapers.wiki.constants import CHASSIS_CONSTRUCTOR_DOMAINS


def _link_text(value: object) -> str:
    if isinstance(value, dict):
        return str(value.get("text", ""))
    return str(value or "")


def _driver_record_key(record: object) -> str | None:
    if not isinstance(record, dict):
        return None

    driver_url = record.get("driver_url")
    if isinstance(driver_url, str) and driver_url:
        return driver_url

    driver = record.get("driver")
    if isinstance(driver, dict):
        url = driver.get("url")
        if isinstance(url, str) and url:
            return url

    return None


def _merge_driver_values(existing: object, incoming: object) -> object:
    if isinstance(existing, dict) and isinstance(incoming, dict):
        return _merge_driver_dict_values(existing, incoming)
    if isinstance(existing, list) and isinstance(incoming, list):
        return _merge_list_values(existing, incoming)
    if existing in (None, "", []):
        return incoming
    return existing


def _merge_driver_dict_values(existing: dict[str, object], incoming: dict[str, object]) -> dict[str, object]:
    normalized_incoming = _normalize_incoming_driver_stats(incoming)
    merged = dict(existing)
    for key, value in normalized_incoming.items():
        if key in {"entries", "starts"}:
            continue
        if key in merged:
            merged[key] = _merge_driver_values(merged[key], value)
        else:
            merged[key] = value
    return merged


def _normalize_incoming_driver_stats(incoming: dict[str, object]) -> dict[str, object]:
    normalized = dict(incoming)
    if "race_entries" not in normalized and "entries" in normalized:
        normalized["race_entries"] = normalized["entries"]
    if "race_starts" not in normalized and "starts" in normalized:
        normalized["race_starts"] = normalized["starts"]
    return normalized


def _merge_list_values(existing: list[object], incoming: list[object]) -> list[object]:
    merged = list(existing)
    seen = {json.dumps(item, sort_keys=True, ensure_ascii=False, default=str) for item in merged}
    for item in incoming:
        serialized = json.dumps(item, sort_keys=True, ensure_ascii=False, default=str)
        if serialized in seen:
            continue
        seen.add(serialized)
        merged.append(item)
    return merged


def _merge_values(existing: object, incoming: object) -> object:
    if isinstance(existing, dict) and isinstance(incoming, dict):
        merged = dict(existing)
        for key, value in incoming.items():
            if key in merged:
                merged[key] = _merge_values(merged[key], value)
            else:
                merged[key] = value
        return merged

    if isinstance(existing, list) and isinstance(incoming, list):
        return _merge_list_values(existing, incoming)

    if existing in (None, "", []):
        return incoming

    return existing


def merge_duplicate_drivers(records: list[object]) -> list[object]:
    merged_records: list[object] = []
    key_to_index: dict[str, int] = {}

    for record in records:
        key = _driver_record_key(record)
        if key is None or not isinstance(record, dict):
            merged_records.append(record)
            continue

        index = key_to_index.get(key)
        if index is None:
            key_to_index[key] = len(merged_records)
            merged_records.append(record)
            continue

        existing = merged_records[index]
        if isinstance(existing, dict):
            merged_records[index] = _merge_driver_values(existing, record)

    return merged_records


def _season_sort_key(record: object) -> tuple[int, str]:
    if not isinstance(record, dict):
        return (1, "")

    season = record.get("season")
    if isinstance(season, int):
        return (0, str(season).zfill(10))

    return (1, "")


def _driver_sort_key(record: object) -> str:
    if not isinstance(record, dict):
        return ""

    driver_value = record.get("driver")
    if isinstance(driver_value, dict):
        driver_text = str(driver_value.get("text", ""))
    else:
        driver_text = str(driver_value or "")

    name_parts = driver_text.split(" ", 1)
    if len(name_parts) == 1:
        return driver_text.strip().casefold()
    return name_parts[1].strip().casefold()


def _constructor_sort_key(record: object) -> str:
    if not isinstance(record, dict):
        return ""
    return _link_text(record.get("constructor")).casefold()


def _team_sort_key(record: object) -> str:
    if not isinstance(record, dict):
        return ""
    return _link_text(record.get("team")).casefold()


def _team_record_key(record: object) -> str | None:
    if not isinstance(record, dict):
        return None

    team = record.get("team")
    if isinstance(team, dict):
        url = team.get("url")
        if isinstance(url, str) and url:
            return url
        text = team.get("text")
        if isinstance(text, str) and text:
            return text.casefold()

    if isinstance(team, str) and team:
        return team.casefold()

    return None


def _team_record_aliases(record: object) -> set[str]:
    if not isinstance(record, dict):
        return set()

    aliases: set[str] = set()
    team = record.get("team")

    if isinstance(team, dict):
        url = team.get("url")
        if isinstance(url, str) and url:
            aliases.add(url)
        text = team.get("text")
        if isinstance(text, str) and text:
            aliases.add(text.casefold())

    if isinstance(team, str) and team:
        aliases.add(team.casefold())

    return aliases


def merge_duplicate_teams(records: list[object]) -> list[object]:
    merged_records: list[object] = []
    key_to_index: dict[str, int] = {}

    for record in records:
        key = _team_record_key(record)
        if key is None or not isinstance(record, dict):
            merged_records.append(record)
            continue

        index = key_to_index.get(key)
        if index is None:
            index = len(merged_records)
            key_to_index[key] = index
            merged_records.append(record)
            for alias in _team_record_aliases(record):
                key_to_index[alias] = index
            continue

        existing = merged_records[index]
        if isinstance(existing, dict):
            merged_record = _merge_values(existing, record)
            merged_records[index] = merged_record
            for alias in _team_record_aliases(merged_record):
                key_to_index[alias] = index

    return merged_records


def _season_years(value: object) -> set[int]:
    years: set[int] = set()
    if isinstance(value, dict):
        year = value.get("year")
        if isinstance(year, int):
            years.add(year)
        return years

    if isinstance(value, list):
        for item in value:
            years.update(_season_years(item))

    return years


def _nest_team_liveries_in_seasons(record: object) -> object:
    formula_one = _formula_one_series(record)
    if formula_one is None:
        return record

    seasons = formula_one.get("seasons")
    liveries = formula_one.get("liveries")
    if not isinstance(seasons, list) or not isinstance(liveries, list):
        return record

    remaining_liveries = _distribute_liveries_across_seasons(seasons, liveries)
    if remaining_liveries:
        formula_one["liveries"] = remaining_liveries
    else:
        formula_one.pop("liveries", None)
    return record


def _formula_one_series(record: object) -> dict[str, object] | None:
    if not isinstance(record, dict):
        return None
    racing_series = record.get("racing_series")
    if not isinstance(racing_series, dict):
        return None
    formula_one = racing_series.get("formula_one")
    return formula_one if isinstance(formula_one, dict) else None


def _distribute_liveries_across_seasons(seasons: list[object], liveries: list[object]) -> list[object]:
    remaining_liveries: list[object] = []
    for livery in liveries:
        if not isinstance(livery, dict):
            remaining_liveries.append(livery)
            continue
        if not _attach_livery_to_matching_seasons(seasons, livery):
            remaining_liveries.append(livery)
    return remaining_liveries


def _attach_livery_to_matching_seasons(seasons: list[object], livery: dict[str, object]) -> bool:
    livery_years = _season_years(livery.get("season"))
    livery_payload = {key: value for key, value in livery.items() if key != "season"}
    matched = False
    for season in seasons:
        if not _season_matches_livery_years(season, livery_years):
            continue
        matched = True
        _append_livery_to_season(season, livery_payload)
    return matched


def _season_matches_livery_years(season: object, livery_years: set[int]) -> bool:
    if not isinstance(season, dict):
        return False
    season_year = season.get("year")
    return isinstance(season_year, int) and season_year in livery_years


def _append_livery_to_season(season: object, livery_payload: dict[str, object]) -> None:
    if not isinstance(season, dict):
        return
    existing_liveries = season.get("liveries")
    if isinstance(existing_liveries, list):
        existing_liveries.append(livery_payload)
        return
    existing_livery = season.pop("livery", None)
    season_liveries: list[object] = []
    if existing_livery is not None:
        season_liveries.append(existing_livery)
    season_liveries.append(livery_payload)
    season["liveries"] = season_liveries


DomainPostProcessor = Callable[[list[object]], list[object]]

DOMAIN_POST_PROCESSORS: dict[str, tuple[DomainPostProcessor, ...]] = {
    "drivers": (
        merge_duplicate_drivers,
        lambda items: sorted(items, key=_driver_sort_key),
    ),
    "teams": (
        merge_duplicate_teams,
        lambda items: [_nest_team_liveries_in_seasons(record) for record in items],
        lambda items: sorted(items, key=_team_sort_key),
    ),
    "seasons": (
        lambda items: sorted(items, key=_season_sort_key),
    ),
}


def post_process_domain_records(domain: str, records: list[object]) -> list[object]:
    processors: list[DomainPostProcessor] = list(DOMAIN_POST_PROCESSORS.get(domain, ()))
    if domain in CHASSIS_CONSTRUCTOR_DOMAINS:
        processors.append(lambda items: sorted(items, key=_constructor_sort_key))

    processed = records
    for processor in processors:
        processed = processor(processed)
    return processed
