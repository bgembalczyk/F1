from __future__ import annotations

import json
import logging
from collections.abc import Callable
from dataclasses import dataclass

from layers.zero.domain_transforms import normalize_driver_stats
from layers.zero.merge_types import DriverRecordModel
from layers.zero.merge_types import LinkValue
from layers.zero.merge_types import SeasonRecordModel
from layers.zero.merge_types import TeamRecordModel
from layers.zero.merge_types import as_record_dict
from scrapers.wiki.constants import CHASSIS_CONSTRUCTOR_DOMAINS

DomainRecordsProcessor = Callable[[list[object]], list[object]]


@dataclass(frozen=True)
class DomainStep:
    name: str
    processor: DomainRecordsProcessor


def _merge_driver_values(existing: object, incoming: object) -> object:
    if isinstance(existing, dict) and isinstance(incoming, dict):
        return _merge_driver_dict_values(existing, incoming)
    if isinstance(existing, list) and isinstance(incoming, list):
        return _merge_list_values(existing, incoming)
    if existing in (None, "", []):
        return incoming
    return existing


def _merge_driver_dict_values(
    existing: dict[str, object],
    incoming: dict[str, object],
) -> dict[str, object]:
    normalized_incoming = normalize_driver_stats(incoming)
    merged = dict(existing)
    for key, value in normalized_incoming.items():
        if key in {"entries", "starts"}:
            continue
        if key in merged:
            merged[key] = _merge_driver_values(merged[key], value)
        else:
            merged[key] = value
    return merged


def _merge_list_values(existing: list[object], incoming: list[object]) -> list[object]:
    merged = list(existing)
    seen = {
        json.dumps(item, sort_keys=True, ensure_ascii=False, default=str)
        for item in merged
    }
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


def _merge_duplicate_drivers(records: list[object]) -> list[object]:
    merged_records: list[object] = []
    key_to_index: dict[str, int] = {}

    for record in records:
        driver_record = DriverRecordModel.from_object(record)
        if driver_record is None:
            merged_records.append(record)
            continue
        key = driver_record.dedupe_key()
        if key is None:
            merged_records.append(driver_record.to_dict())
            continue

        index = key_to_index.get(key)
        if index is None:
            key_to_index[key] = len(merged_records)
            merged_records.append(driver_record.to_dict())
            continue

        existing = merged_records[index]
        existing_driver = DriverRecordModel.from_object(existing)
        if existing_driver is None:
            continue
        merged_records[index] = _merge_driver_values(
            existing_driver.to_dict(),
            driver_record.to_dict(),
        )

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


def _link_text(value: object) -> str:
    if (link := LinkValue.from_object(value)) is not None:
        return link.text
    return str(value or "")


def _constructor_sort_key(record: object) -> str:
    if not isinstance(record, dict):
        return ""
    return _link_text(record.get("constructor")).casefold()


def _team_sort_key(record: object) -> str:
    if not isinstance(record, dict):
        return ""
    return _link_text(record.get("team")).casefold()


def _merge_duplicate_teams(records: list[object]) -> list[object]:
    merged_records: list[object] = []
    key_to_index: dict[str, int] = {}

    for record in records:
        team_record = TeamRecordModel.from_object(record)
        if team_record is None:
            merged_records.append(record)
            continue
        key = team_record.dedupe_key()
        if key is None:
            merged_records.append(team_record.to_dict())
            continue

        index = key_to_index.get(key)
        if index is None:
            index = len(merged_records)
            key_to_index[key] = index
            merged_records.append(team_record.to_dict())
            for alias in team_record.aliases():
                key_to_index[alias] = index
            continue

        existing = merged_records[index]
        existing_team = TeamRecordModel.from_object(existing)
        if existing_team is None:
            continue

        merged_record = _merge_values(existing_team.to_dict(), team_record.to_dict())
        merged_records[index] = merged_record
        merged_team = TeamRecordModel.from_object(merged_record)
        if merged_team is None:
            continue
        for alias in merged_team.aliases():
            key_to_index[alias] = index

    return merged_records


def _season_years(value: object) -> set[int]:
    years: set[int] = set()
    if (season := SeasonRecordModel.from_object(value)) is not None:
        if (year := season.year()) is not None:
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
    record_dict = as_record_dict(record)
    if record_dict is None:
        return None
    racing_series = as_record_dict(record_dict.get("racing_series"))
    if racing_series is None:
        return None
    return as_record_dict(racing_series.get("formula_one"))


def _distribute_liveries_across_seasons(
    seasons: list[object],
    liveries: list[object],
) -> list[object]:
    remaining_liveries: list[object] = []
    for livery in liveries:
        if not isinstance(livery, dict):
            remaining_liveries.append(livery)
            continue
        if not _attach_livery_to_matching_seasons(seasons, livery):
            remaining_liveries.append(livery)
    return remaining_liveries


def _attach_livery_to_matching_seasons(
    seasons: list[object],
    livery: dict[str, object],
) -> bool:
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
    season_record = SeasonRecordModel.from_object(season)
    if season_record is None:
        return False
    season_year = season_record.year()
    return season_year is not None and season_year in livery_years


def _append_livery_to_season(season: object, livery_payload: dict[str, object]) -> None:
    season_record = SeasonRecordModel.from_object(season)
    if season_record is None:
        return
    season_record.append_livery(livery_payload)


def _sort_drivers_by_name(items: list[object]) -> list[object]:
    return sorted(items, key=_driver_sort_key)


def _sort_constructors_by_name(items: list[object]) -> list[object]:
    return sorted(items, key=_constructor_sort_key)


def _nest_team_liveries(items: list[object]) -> list[object]:
    return [_nest_team_liveries_in_seasons(record) for record in items]


def _sort_teams_by_name(items: list[object]) -> list[object]:
    return sorted(items, key=_team_sort_key)


def _sort_seasons_by_year(items: list[object]) -> list[object]:
    return sorted(items, key=_season_sort_key)


def build_domain_postprocess_steps() -> dict[str, tuple[DomainStep, ...]]:
    steps: dict[str, tuple[DomainStep, ...]] = {
        "drivers": (
            DomainStep("merge_duplicate_drivers", _merge_duplicate_drivers),
            DomainStep("sort_drivers_by_name", _sort_drivers_by_name),
        ),
        "teams": (
            DomainStep("merge_duplicate_teams", _merge_duplicate_teams),
            DomainStep("nest_team_liveries", _nest_team_liveries),
            DomainStep("sort_teams_by_name", _sort_teams_by_name),
        ),
        "seasons": (DomainStep("sort_seasons_by_year", _sort_seasons_by_year),),
    }
    for constructor_domain in CHASSIS_CONSTRUCTOR_DOMAINS:
        steps.setdefault(
            constructor_domain,
            (DomainStep("sort_constructors_by_name", _sort_constructors_by_name),),
        )
    return steps


def _records_debug_summary(records: list[object]) -> str:
    sample = records[0] if records else None
    sample_type = type(sample).__name__ if sample is not None else "none"
    return f"count={len(records)}, first_type={sample_type}"


def execute_domain_steps(
    *,
    domain: str,
    step_group: str,
    records: list[object],
    steps: tuple[DomainStep, ...],
    logger: logging.Logger,
) -> list[object]:
    current = records
    executed_steps: list[str] = []
    for step in steps:
        before_summary = _records_debug_summary(current)
        current = step.processor(current)
        after_summary = _records_debug_summary(current)
        executed_steps.append(step.name)
        logger.debug(
            "Domain '%s' %s step '%s': %s -> %s",
            domain,
            step_group,
            step.name,
            before_summary,
            after_summary,
        )

    logger.debug(
        "Domain '%s' %s steps executed (order=%s, final_count=%s)",
        domain,
        step_group,
        executed_steps,
        len(current),
    )
    return current
