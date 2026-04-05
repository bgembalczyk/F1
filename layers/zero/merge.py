import logging
import re
from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

from layers.orchestration.types import CONSTRUCTOR_STATUS_ACTIVE
from layers.orchestration.types import CONSTRUCTOR_STATUS_FORMER
from layers.path_resolver import PathResolver
from layers.zero.merge_types import DriverRecordModel
from layers.zero.merge_types import EngineRecordModel
from layers.zero.merge_types import LinkValue
from layers.zero.merge_types import RaceRecordModel
from layers.zero.merge_types import SeasonRecordModel
from layers.zero.merge_types import TeamRecordModel
from layers.zero.record_merge_ops import (
    merge_driver_dict_values as _merge_driver_dict_values_impl,
)
from layers.zero.record_merge_ops import (
    merge_driver_values as _merge_driver_values_impl,
)
from layers.zero.record_merge_ops import merge_list_values as _merge_list_values_impl
from layers.zero.record_merge_ops import merge_values as _merge_values_impl
from layers.zero.source_routing import (
    iter_mergeable_domain_dirs as _iter_mergeable_domain_dirs_impl,
)
from layers.zero.source_routing import load_domain_records as _load_domain_records_impl
from layers.zero.source_routing import (
    write_merged_domain_records as _write_merged_domain_records_impl,
)
from scrapers.wiki.constants import CHASSIS_CONSTRUCTOR_DOMAINS
from scrapers.wiki.constants import CIRCUITS_FORMULA_ONE_FIELDS
from scrapers.wiki.constants import CONSTRUCTORS_FORMULA_ONE_FIELDS
from scrapers.wiki.constants import ENGINES_FORMULA_ONE_FIELDS
from scrapers.wiki.constants import FORMULA_ONE_SERIES
from scrapers.wiki.constants import GRANDS_PRIX_FORMULA_ONE_FIELDS
from scrapers.wiki.constants import RED_FLAG_FIELDS
from scrapers.wiki.sources_registry import DRIVER_FATALITIES_SOURCE
from scrapers.wiki.sources_registry import DRIVERS_SOURCE
from scrapers.wiki.sources_registry import ENGINE_MANUFACTURERS_INDIANAPOLIS_ONLY_SOURCE
from scrapers.wiki.sources_registry import ENGINE_MANUFACTURERS_SOURCE
from scrapers.wiki.sources_registry import FEMALE_DRIVERS_SOURCE
from scrapers.wiki.sources_registry import FORMER_CONSTRUCTORS_SOURCE
from scrapers.wiki.sources_registry import INDIANAPOLIS_ONLY_CONSTRUCTORS_SOURCE
from scrapers.wiki.sources_registry import INDIANAPOLIS_ONLY_ENGINES_SOURCE
from scrapers.wiki.sources_registry import PRIVATEER_TEAMS_SOURCE
from scrapers.wiki.sources_registry import RED_FLAGGED_NON_CHAMPIONSHIP_SOURCE
from scrapers.wiki.sources_registry import RED_FLAGGED_WORLD_CHAMPIONSHIP_SOURCE
from scrapers.wiki.sources_registry import SPONSORSHIP_LIVERIES_SOURCE
from scrapers.wiki.sources_registry import TYRE_MANUFACTURERS_SOURCE
from scrapers.wiki.sources_registry import resolve_list_filename
from scrapers.wiki.sources_registry import validate_sources_registry_consistency

RecordTransformHandler = Callable[
    [str, str, dict[str, object]],
    dict[str, object],
]
DomainRecordsProcessor = Callable[[list[object]], list[object]]

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DomainStep:
    name: str
    processor: DomainRecordsProcessor


@dataclass(frozen=True)
class DomainPipelineConfig:
    transformers: dict[str, tuple[RecordTransformHandler, ...]] = field(
        default_factory=dict,
    )
    postprocessors: tuple[DomainStep, ...] = ()
    records_normalizer: DomainRecordsProcessor | None = None


def _build_racing_series(formula_one: dict[str, object]) -> dict[str, object]:
    sorted_formula_one = {key: formula_one[key] for key in sorted(formula_one)}
    return {"formula_one": sorted_formula_one}


def _move_fields_to_formula_one(
    transformed: dict[str, object],
    fields: set[str],
) -> None:
    formula_one = {key: transformed.pop(key) for key in fields if key in transformed}
    if not formula_one:
        return
    transformed["racing_series"] = _build_racing_series(formula_one)


def _link_text(value: object) -> str:
    if (link := LinkValue.from_object(value)) is not None:
        return link.text
    return str(value or "")


def _extract_red_flag(record: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in record.items() if key in RED_FLAG_FIELDS}


def _pop_red_flag_fields(record: dict[str, object]) -> None:
    for key in RED_FLAG_FIELDS:
        record.pop(key, None)


def _transform_record(domain: str, source_name: str, record: object) -> object:
    if not isinstance(record, dict):
        return record

    canonical_source_name = resolve_list_filename(source_name)
    transformed = dict(record)
    for handler in _resolve_record_transform_handlers(domain, canonical_source_name):
        transformed = handler(domain, canonical_source_name, transformed)
    return transformed


def _tyre_manufacturers_handler(
    domain: str,
    source_name: str,
    record: dict[str, object],
) -> dict[str, object]:
    _ = domain
    return _transform_tyre_manufacturers(source_name, record)


def _constructor_domain_handler(
    domain: str,
    source_name: str,
    record: dict[str, object],
) -> dict[str, object]:
    return _transform_constructor_domain(domain, source_name, record)


def _circuits_domain_handler(
    domain: str,
    source_name: str,
    record: dict[str, object],
) -> dict[str, object]:
    _ = source_name
    return _transform_circuits_domain(domain, record)


def _engines_domain_handler(
    domain: str,
    source_name: str,
    record: dict[str, object],
) -> dict[str, object]:
    return _transform_engines_domain(domain, source_name, record)


def _grands_prix_domain_handler(
    domain: str,
    source_name: str,
    record: dict[str, object],
) -> dict[str, object]:
    _ = source_name
    return _transform_grands_prix_domain(domain, record)


def _teams_domain_handler(
    domain: str,
    source_name: str,
    record: dict[str, object],
) -> dict[str, object]:
    return _transform_teams_domain(domain, source_name, record)


def _drivers_domain_handler(
    domain: str,
    source_name: str,
    record: dict[str, object],
) -> dict[str, object]:
    return _transform_drivers_domain(domain, source_name, record)


def _races_domain_handler(
    domain: str,
    source_name: str,
    record: dict[str, object],
) -> dict[str, object]:
    return _transform_races_domain(domain, source_name, record)


DEFAULT_SOURCE_PIPELINE = "*"


def _normalize_engine_records(records: list[object]) -> list[object]:
    return [
        engine_record.to_dict()
        if (engine_record := EngineRecordModel.from_object(record)) is not None
        else record
        for record in records
    ]


def _normalize_race_records(records: list[object]) -> list[object]:
    return [
        race_record.to_dict()
        if (race_record := RaceRecordModel.from_object(record)) is not None
        else record
        for record in records
    ]


DOMAIN_PIPELINE_CONFIGS: dict[str, DomainPipelineConfig] = {
    "*": DomainPipelineConfig(
        transformers={
            TYRE_MANUFACTURERS_SOURCE: (_tyre_manufacturers_handler,),
        },
    ),
    "constructors": DomainPipelineConfig(
        transformers={DEFAULT_SOURCE_PIPELINE: (_constructor_domain_handler,)},
    ),
    "constructor": DomainPipelineConfig(
        transformers={DEFAULT_SOURCE_PIPELINE: (_constructor_domain_handler,)},
    ),
    "chassis": DomainPipelineConfig(
        transformers={DEFAULT_SOURCE_PIPELINE: (_constructor_domain_handler,)},
    ),
    "circuits": DomainPipelineConfig(
        transformers={DEFAULT_SOURCE_PIPELINE: (_circuits_domain_handler,)},
    ),
    "engines": DomainPipelineConfig(
        transformers={DEFAULT_SOURCE_PIPELINE: (_engines_domain_handler,)},
        records_normalizer=_normalize_engine_records,
    ),
    "grands_prix": DomainPipelineConfig(
        transformers={DEFAULT_SOURCE_PIPELINE: (_grands_prix_domain_handler,)},
    ),
    "teams": DomainPipelineConfig(
        transformers={DEFAULT_SOURCE_PIPELINE: (_teams_domain_handler,)},
    ),
    "drivers": DomainPipelineConfig(
        transformers={DEFAULT_SOURCE_PIPELINE: (_drivers_domain_handler,)},
    ),
    "races": DomainPipelineConfig(
        transformers={DEFAULT_SOURCE_PIPELINE: (_races_domain_handler,)},
        records_normalizer=_normalize_race_records,
    ),
}

validate_sources_registry_consistency()


def _resolve_record_transform_handlers(
    domain: str,
    source_name: str,
) -> tuple[RecordTransformHandler, ...]:
    global_handlers = DOMAIN_PIPELINE_CONFIGS.get(
        "*",
        DomainPipelineConfig(),
    ).transformers
    domain_handlers = DOMAIN_PIPELINE_CONFIGS.get(
        domain,
        DomainPipelineConfig(),
    ).transformers

    resolved: list[RecordTransformHandler] = [
        *global_handlers.get(DEFAULT_SOURCE_PIPELINE, ()),
        *global_handlers.get(source_name, ()),
    ]
    domain_pipeline = domain_handlers.get(source_name)
    if domain_pipeline is None:
        domain_pipeline = domain_handlers.get(DEFAULT_SOURCE_PIPELINE, ())
    resolved.extend(domain_pipeline)
    return tuple(resolved)


def _transform_tyre_manufacturers(
    source_name: str,
    transformed: dict[str, object],
) -> dict[str, object]:
    if source_name != TYRE_MANUFACTURERS_SOURCE:
        return transformed

    if "manufacturers" in transformed:
        transformed["tyre_manufacturers"] = transformed.pop("manufacturers")
    seasons = transformed.get("seasons")
    if isinstance(seasons, list) and len(seasons) == 1:
        transformed["season"] = transformed.pop("seasons")[0]
    return transformed


def _transform_constructor_domain(
    domain: str,
    source_name: str,
    transformed: dict[str, object],
) -> dict[str, object]:
    if domain not in CHASSIS_CONSTRUCTOR_DOMAINS:
        return transformed

    if source_name == INDIANAPOLIS_ONLY_CONSTRUCTORS_SOURCE:
        return _transform_indianapolis_only_constructor(transformed)
    if source_name == FORMER_CONSTRUCTORS_SOURCE:
        return _transform_former_constructor(transformed)

    constructor_fields = set(CONSTRUCTORS_FORMULA_ONE_FIELDS)
    if domain == "constructors" and re.fullmatch(
        r"f1_constructors_\d{4}\.json",
        source_name,
    ):
        constructor_fields.discard("engine")

    _move_fields_to_formula_one(transformed, constructor_fields)
    _ensure_constructor_status(transformed)
    return transformed


def _transform_indianapolis_only_constructor(
    transformed: dict[str, object],
) -> dict[str, object]:
    return {
        "constructor": {
            "text": transformed.get("constructor"),
            "url": transformed.get("constructor_url"),
        },
        "racing_series": {
            "AAA_national_championship": [],
            "formula_one": {
                "status": CONSTRUCTOR_STATUS_FORMER,
                "indianapolis_only": True,
            },
        },
    }


def _transform_former_constructor(transformed: dict[str, object]) -> dict[str, object]:
    constructor = transformed.get("constructor")
    formula_one = {
        key: value for key, value in transformed.items() if key != "constructor"
    }
    formula_one["status"] = CONSTRUCTOR_STATUS_FORMER
    return {
        "constructor": constructor,
        "racing_series": _build_racing_series(formula_one),
    }


def _ensure_constructor_status(transformed: dict[str, object]) -> None:
    if "racing_series" not in transformed:
        transformed["status"] = CONSTRUCTOR_STATUS_ACTIVE
        transformed["series"] = FORMULA_ONE_SERIES.copy()
        return

    racing_series = transformed.get("racing_series")
    if not isinstance(racing_series, dict):
        racing_series = {}
        transformed["racing_series"] = racing_series
    formula_one = racing_series.setdefault("formula_one", {})
    formula_one.setdefault("status", CONSTRUCTOR_STATUS_ACTIVE)


def _transform_circuits_domain(
    domain: str,
    transformed: dict[str, object],
) -> dict[str, object]:
    if domain != "circuits":
        return transformed
    _move_fields_to_formula_one(transformed, CIRCUITS_FORMULA_ONE_FIELDS)
    if "racing_series" not in transformed:
        transformed["series"] = FORMULA_ONE_SERIES.copy()
    return transformed


def _transform_engines_domain(
    domain: str,
    source_name: str,
    transformed: dict[str, object],
) -> dict[str, object]:
    if domain != "engines":
        return transformed
    if source_name in (
        INDIANAPOLIS_ONLY_ENGINES_SOURCE,
        ENGINE_MANUFACTURERS_INDIANAPOLIS_ONLY_SOURCE,
    ):
        transformed["racing_series"] = {
            "AAA_national_championship": [],
            "formula_one": {
                "status": CONSTRUCTOR_STATUS_FORMER,
                "indianapolis_only": True,
            },
        }
    elif source_name == ENGINE_MANUFACTURERS_SOURCE:
        _move_fields_to_formula_one(transformed, ENGINES_FORMULA_ONE_FIELDS)
    return transformed


def _transform_grands_prix_domain(
    domain: str,
    transformed: dict[str, object],
) -> dict[str, object]:
    if domain == "grands_prix":
        _move_fields_to_formula_one(transformed, GRANDS_PRIX_FORMULA_ONE_FIELDS)
    return transformed


def _transform_teams_domain(
    domain: str,
    source_name: str,
    transformed: dict[str, object],
) -> dict[str, object]:
    if domain != "teams":
        return transformed
    if re.fullmatch(r"f1_constructors_\d{4}\.json", source_name):
        transformed = {
            "team": transformed.get("constructor"),
            "racing_series": _build_racing_series({**transformed}),
        }
    if source_name == SPONSORSHIP_LIVERIES_SOURCE and "liveries" in transformed:
        transformed["racing_series"] = _build_racing_series(
            {"liveries": transformed.pop("liveries")},
        )
    if source_name == PRIVATEER_TEAMS_SOURCE:
        formula_one = {
            key: transformed.pop(key) for key in ("seasons",) if key in transformed
        }
        formula_one["privateer"] = True
        transformed["racing_series"] = _build_racing_series(formula_one)
    return transformed


def _transform_drivers_domain(
    domain: str,
    source_name: str,
    transformed: dict[str, object],
) -> dict[str, object]:
    if domain != "drivers":
        return transformed
    if source_name == DRIVERS_SOURCE:
        return _transform_f1_driver(transformed)
    if source_name == FEMALE_DRIVERS_SOURCE:
        return _transform_female_driver(transformed)
    if source_name == DRIVER_FATALITIES_SOURCE:
        _attach_driver_death_data(transformed)
    return transformed


def _transform_f1_driver(transformed: dict[str, object]) -> dict[str, object]:
    driver_record = DriverRecordModel(raw=transformed)
    driver, nationality = driver_record.extract_identity()
    formula_one = driver_record.extract_series_stats().to_dict()
    return {
        "driver": driver,
        "nationality": nationality,
        "racing_series": _build_racing_series(formula_one),
    }


def _transform_female_driver(transformed: dict[str, object]) -> dict[str, object]:
    driver_record = DriverRecordModel(raw=transformed)
    driver, _ = driver_record.extract_identity()
    formula_one = driver_record.extract_series_stats().to_dict()
    return {
        "driver": driver,
        "gender": "female",
        "racing_series": _build_racing_series(formula_one),
    }


def _attach_driver_death_data(transformed: dict[str, object]) -> None:
    death_fields = {
        key: transformed.pop(key) for key in ("date", "age") if key in transformed
    }
    crash_fields = {
        key: transformed.pop(key)
        for key in ("event", "circuit", "car", "session")
        if key in transformed
    }
    transformed["death"] = {**death_fields, "crash": crash_fields}


def _transform_races_domain(
    domain: str,
    source_name: str,
    transformed: dict[str, object],
) -> dict[str, object]:
    if domain != "races":
        return transformed
    if source_name == RED_FLAGGED_WORLD_CHAMPIONSHIP_SOURCE:
        transformed["championship"] = True
    if source_name == RED_FLAGGED_NON_CHAMPIONSHIP_SOURCE:
        transformed["championship"] = False
    transformed["red_flag"] = _extract_red_flag(transformed)
    _pop_red_flag_fields(transformed)
    return transformed


def _iter_transformed_records(
    domain: str,
    source_name: str,
    payload: object,
) -> list[object]:
    domain_config = DOMAIN_PIPELINE_CONFIGS.get(domain, DomainPipelineConfig())

    if isinstance(payload, list):
        transformed = [_transform_record(domain, source_name, item) for item in payload]
        if domain_config.records_normalizer is None:
            return transformed
        return domain_config.records_normalizer(transformed)

    transformed_record = _transform_record(domain, source_name, payload)
    records = [transformed_record]
    if domain_config.records_normalizer is None:
        return records
    return domain_config.records_normalizer(records)


def _merge_driver_values(existing: object, incoming: object) -> object:
    return _merge_driver_values_impl(existing, incoming)


def _merge_driver_dict_values(
    existing: dict[str, object],
    incoming: dict[str, object],
) -> dict[str, object]:
    return _merge_driver_dict_values_impl(existing, incoming)


def _merge_list_values(existing: list[object], incoming: list[object]) -> list[object]:
    return _merge_list_values_impl(existing, incoming)


def _merge_values(existing: object, incoming: object) -> object:
    return _merge_values_impl(existing, incoming)


def _merge_duplicate_drivers(records: list[object]) -> list[object]:
    """Aktywna, gdy domena to `drivers`."""
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


def _engine_sort_key(record: object) -> str:
    if not isinstance(record, dict):
        return ""
    return _link_text(record.get("manufacturer")).casefold()


def _merge_duplicate_teams(records: list[object]) -> list[object]:
    """Aktywna, gdy domena to `teams`."""
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
    if not isinstance(record, dict):
        return None
    racing_series = record.get("racing_series")
    if not isinstance(racing_series, dict):
        return None
    formula_one = racing_series.get("formula_one")
    if not isinstance(formula_one, dict):
        return None
    return formula_one


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


def merge_layer_zero_raw_outputs(base_wiki_dir: Path) -> None:
    layer_zero_dir = base_wiki_dir / "layers" / "0_layer"
    if not layer_zero_dir.exists():
        return

    resolver = PathResolver(layer_zero_root=layer_zero_dir)

    for domain_dir in _iter_mergeable_domain_dirs(layer_zero_dir, resolver):
        merged_records = _load_domain_records(domain_dir, resolver)
        if not merged_records:
            continue
        merged_records = _post_process_domain_records(domain_dir.name, merged_records)
        _write_merged_domain_records(domain_dir, merged_records, resolver)


def _iter_mergeable_domain_dirs(
    layer_zero_dir: Path,
    resolver: PathResolver,
) -> list[Path]:
    return _iter_mergeable_domain_dirs_impl(layer_zero_dir, resolver)


def _load_domain_records(domain_dir: Path, resolver: PathResolver) -> list[object]:
    return _load_domain_records_impl(
        domain_dir,
        resolver,
        transform_records=_iter_transformed_records,
    )


def _sort_drivers_by_name(items: list[object]) -> list[object]:
    return sorted(items, key=_driver_sort_key)


def _sort_constructors_by_name(items: list[object]) -> list[object]:
    return sorted(items, key=_constructor_sort_key)


def _nest_team_liveries(items: list[object]) -> list[object]:
    return [_nest_team_liveries_in_seasons(record) for record in items]


def _sort_teams_by_name(items: list[object]) -> list[object]:
    return sorted(items, key=_team_sort_key)


def _sort_engines_by_manufacturer(items: list[object]) -> list[object]:
    return sorted(items, key=_engine_sort_key)


def _sort_seasons_by_year(items: list[object]) -> list[object]:
    return sorted(items, key=_season_sort_key)


DOMAIN_POSTPROCESS_STEPS_BY_DOMAIN: dict[str, tuple[DomainStep, ...]] = {
    "drivers": (
        DomainStep("merge_duplicate_drivers", _merge_duplicate_drivers),
        DomainStep("sort_drivers_by_name", _sort_drivers_by_name),
    ),
    "teams": (
        DomainStep("merge_duplicate_teams", _merge_duplicate_teams),
        DomainStep("nest_team_liveries", _nest_team_liveries),
        DomainStep("sort_teams_by_name", _sort_teams_by_name),
    ),
    "engines": (
        DomainStep("sort_engines_by_manufacturer", _sort_engines_by_manufacturer),
    ),
    "seasons": (DomainStep("sort_seasons_by_year", _sort_seasons_by_year),),
}

for _constructor_domain in CHASSIS_CONSTRUCTOR_DOMAINS:
    DOMAIN_POSTPROCESS_STEPS_BY_DOMAIN.setdefault(
        _constructor_domain,
        (DomainStep("sort_constructors_by_name", _sort_constructors_by_name),),
    )

for _domain, _postprocessors in DOMAIN_POSTPROCESS_STEPS_BY_DOMAIN.items():
    existing = DOMAIN_PIPELINE_CONFIGS.get(_domain, DomainPipelineConfig())
    DOMAIN_PIPELINE_CONFIGS[_domain] = DomainPipelineConfig(
        transformers=existing.transformers,
        postprocessors=_postprocessors,
        records_normalizer=existing.records_normalizer,
    )

for _domain, _config in tuple(DOMAIN_PIPELINE_CONFIGS.items()):
    DOMAIN_PIPELINE_CONFIGS[_domain] = DomainPipelineConfig(
        transformers=_config.transformers,
        postprocessors=tuple(_config.postprocessors),
        records_normalizer=_config.records_normalizer,
    )


def _records_debug_summary(records: list[object]) -> str:
    sample = records[0] if records else None
    sample_type = type(sample).__name__ if sample is not None else "none"
    return f"count={len(records)}, first_type={sample_type}"


def _execute_domain_steps(
    domain: str,
    step_group: str,
    records: list[object],
    steps: tuple[DomainStep, ...],
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


def _post_process_domain_records(domain: str, records: list[object]) -> list[object]:
    postprocessors = DOMAIN_PIPELINE_CONFIGS.get(
        domain,
        DomainPipelineConfig(),
    ).postprocessors
    return _execute_domain_steps(
        domain=domain,
        step_group="postprocess",
        records=records,
        steps=postprocessors,
    )


def _write_merged_domain_records(
    domain_dir: Path,
    merged_records: list[object],
    resolver: PathResolver,
) -> None:
    _write_merged_domain_records_impl(domain_dir, merged_records, resolver)
