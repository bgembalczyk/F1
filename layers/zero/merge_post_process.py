import json
import logging
from collections.abc import Callable
from dataclasses import dataclass

from layers.zero.merge_types import DriverRecordModel
from layers.zero.merge_types import TeamRecordModel
from layers.zero.merge_types import as_record_dict
from scrapers.wiki.constants import CHASSIS_CONSTRUCTOR_DOMAINS

DomainRecordsProcessor = Callable[[list[object]], list[object]]
logger = logging.getLogger(__name__)


def _link_text(value: object) -> str:
    if isinstance(value, dict):
        return str(value.get("text", ""))
    return str(value or "")


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
    season_dict = as_record_dict(season)
    if season_dict is None:
        return False
    season_year = season_dict.get("year")
    return isinstance(season_year, int) and season_year in livery_years


def _append_livery_to_season(season: object, livery_payload: dict[str, object]) -> None:
    season_dict = as_record_dict(season)
    if season_dict is None:
        return
    existing_liveries = season_dict.get("liveries")
    if isinstance(existing_liveries, list):
        existing_liveries.append(livery_payload)
        return
    existing_livery = season_dict.pop("livery", None)
    season_liveries: list[object] = []
    if existing_livery is not None:
        season_liveries.append(existing_livery)
    season_liveries.append(livery_payload)
    season_dict["liveries"] = season_liveries


@dataclass(frozen=True)
class DomainPostProcessStrategy:
    name: str
    activation_condition: Callable[[str], bool]
    processor: DomainRecordsProcessor

    def is_active(self, domain: str) -> bool:
        return self.activation_condition(domain)


def _is_drivers_domain(domain: str) -> bool:
    return domain == "drivers"


def _is_constructor_domain(domain: str) -> bool:
    return domain in CHASSIS_CONSTRUCTOR_DOMAINS


def _is_teams_domain(domain: str) -> bool:
    return domain == "teams"


def _is_seasons_domain(domain: str) -> bool:
    return domain == "seasons"


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


DOMAIN_POST_PROCESS_STRATEGIES: tuple[DomainPostProcessStrategy, ...] = (
    DomainPostProcessStrategy(
        name="merge_duplicate_drivers",
        activation_condition=_is_drivers_domain,
        processor=_merge_duplicate_drivers,
    ),
    DomainPostProcessStrategy(
        name="sort_drivers_by_name",
        activation_condition=_is_drivers_domain,
        processor=_sort_drivers_by_name,
    ),
    DomainPostProcessStrategy(
        name="sort_constructors_by_name",
        activation_condition=_is_constructor_domain,
        processor=_sort_constructors_by_name,
    ),
    DomainPostProcessStrategy(
        name="merge_duplicate_teams",
        activation_condition=_is_teams_domain,
        processor=_merge_duplicate_teams,
    ),
    DomainPostProcessStrategy(
        name="nest_team_liveries",
        activation_condition=_is_teams_domain,
        processor=_nest_team_liveries,
    ),
    DomainPostProcessStrategy(
        name="sort_teams_by_name",
        activation_condition=_is_teams_domain,
        processor=_sort_teams_by_name,
    ),
    DomainPostProcessStrategy(
        name="sort_seasons_by_year",
        activation_condition=_is_seasons_domain,
        processor=_sort_seasons_by_year,
    ),
)


def _iter_active_domain_post_process_strategies(
    domain: str,
) -> list[DomainPostProcessStrategy]:
    return [
        strategy
        for strategy in DOMAIN_POST_PROCESS_STRATEGIES
        if strategy.is_active(domain)
    ]


def _records_debug_summary(records: list[object]) -> str:
    sample = records[0] if records else None
    sample_type = type(sample).__name__ if sample is not None else "none"
    return f"count={len(records)}, first_type={sample_type}"


def post_process_domain_records(domain: str, records: list[object]) -> list[object]:
    merged_records = records
    for strategy in _iter_active_domain_post_process_strategies(domain):
        before_summary = _records_debug_summary(merged_records)
        merged_records = strategy.processor(merged_records)
        after_summary = _records_debug_summary(merged_records)
        logger.debug(
            "Domain post-process strategy '%s' applied for domain '%s': %s -> %s",
            strategy.name,
            domain,
            before_summary,
            after_summary,
        )
    return merged_records
