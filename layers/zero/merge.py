import json
import logging
import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from layers.path_resolver import PathResolver
from layers.zero.merge_types import DriverRecordModel
from layers.zero.merge_types import EngineRecordModel
from layers.zero.merge_types import RaceRecordModel
from layers.zero.merge_types import TeamRecordModel
from layers.zero.merge_types import as_record_dict
from layers.zero.source_classifier import SourceClassification
from layers.zero.source_classifier import SourceMetadata
from layers.zero.source_classifier import classify_source
from scrapers.wiki.constants import CHASSIS_CONSTRUCTOR_DOMAINS
from scrapers.wiki.constants import CIRCUITS_FORMULA_ONE_FIELDS
from scrapers.wiki.constants import CONSTRUCTORS_FORMULA_ONE_FIELDS
from scrapers.wiki.constants import ENGINES_FORMULA_ONE_FIELDS
from scrapers.wiki.constants import FORMULA_ONE_SERIES
from scrapers.wiki.constants import GRANDS_PRIX_FORMULA_ONE_FIELDS
from scrapers.wiki.constants import RED_FLAG_FIELDS
from scrapers.wiki.sources_registry import TYRE_MANUFACTURERS_SOURCE
from scrapers.wiki.sources_registry import validate_sources_registry_consistency

RecordTransformHandler = Callable[
    [str, str, dict[str, object], SourceClassification],
    dict[str, object],
]
DomainRecordsProcessor = Callable[[list[object]], list[object]]

logger = logging.getLogger(__name__)


def _build_racing_series(formula_one: dict[str, object]) -> dict[str, object]:
    return {"formula_one": formula_one}


def _move_fields_to_formula_one(
    transformed: dict[str, object],
    fields: set[str],
) -> None:
    formula_one = {key: transformed.pop(key) for key in fields if key in transformed}
    if not formula_one:
        return
    transformed["racing_series"] = _build_racing_series(formula_one)


def _link_text(value: object) -> str:
    if isinstance(value, dict):
        return str(value.get("text", ""))
    return str(value or "")


def _normalize_driver_series_stats(formula_one: dict[str, object]) -> dict[str, object]:
    normalized = dict(formula_one)
    if "race_entries" not in normalized and "entries" in normalized:
        normalized["race_entries"] = normalized.pop("entries")
    else:
        normalized.pop("entries", None)

    if "race_starts" not in normalized and "starts" in normalized:
        normalized["race_starts"] = normalized.pop("starts")
    else:
        normalized.pop("starts", None)

    return normalized


def _extract_red_flag(record: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in record.items() if key in RED_FLAG_FIELDS}


def _pop_red_flag_fields(record: dict[str, object]) -> None:
    for key in RED_FLAG_FIELDS:
        record.pop(key, None)


def _transform_record(
    domain: str,
    source_name: str,
    classification: SourceClassification,
    record: object,
) -> object:
    if not isinstance(record, dict):
        return record

    transformed = dict(record)
    for handler in _resolve_record_transform_handlers(domain, source_name):
        transformed = handler(domain, source_name, transformed, classification)
    return transformed


def _tyre_manufacturers_handler(
    domain: str,
    source_name: str,
    record: dict[str, object],
    classification: SourceClassification | None = None,
) -> dict[str, object]:
    _ = classification
    _ = domain
    return _transform_tyre_manufacturers(source_name, record)


def _constructor_domain_handler(
    domain: str,
    source_name: str,
    record: dict[str, object],
    classification: SourceClassification | None = None,
) -> dict[str, object]:
    if classification is None:
        classification = classify_source(
            SourceMetadata(domain=domain, source_name=source_name),
        )
    return _transform_constructor_domain(domain, source_name, record, classification)


def _circuits_domain_handler(
    domain: str,
    source_name: str,
    record: dict[str, object],
    classification: SourceClassification | None = None,
) -> dict[str, object]:
    _ = classification
    _ = source_name
    return _transform_circuits_domain(domain, record)


def _engines_domain_handler(
    domain: str,
    source_name: str,
    record: dict[str, object],
    classification: SourceClassification | None = None,
) -> dict[str, object]:
    if classification is None:
        classification = classify_source(
            SourceMetadata(domain=domain, source_name=source_name),
        )
    return _transform_engines_domain(domain, source_name, record, classification)


def _grands_prix_domain_handler(
    domain: str,
    source_name: str,
    record: dict[str, object],
    classification: SourceClassification | None = None,
) -> dict[str, object]:
    _ = classification
    _ = source_name
    return _transform_grands_prix_domain(domain, record)


def _teams_domain_handler(
    domain: str,
    source_name: str,
    record: dict[str, object],
    classification: SourceClassification | None = None,
) -> dict[str, object]:
    if classification is None:
        classification = classify_source(
            SourceMetadata(domain=domain, source_name=source_name),
        )
    return _transform_teams_domain(domain, source_name, record, classification)


def _drivers_domain_handler(
    domain: str,
    source_name: str,
    record: dict[str, object],
    classification: SourceClassification | None = None,
) -> dict[str, object]:
    if classification is None:
        classification = classify_source(
            SourceMetadata(domain=domain, source_name=source_name),
        )
    return _transform_drivers_domain(domain, source_name, record, classification)


def _races_domain_handler(
    domain: str,
    source_name: str,
    record: dict[str, object],
    classification: SourceClassification | None = None,
) -> dict[str, object]:
    if classification is None:
        classification = classify_source(
            SourceMetadata(domain=domain, source_name=source_name),
        )
    return _transform_races_domain(domain, source_name, record, classification)


DEFAULT_SOURCE_PIPELINE = "*"


def _build_transform_pipelines() -> dict[
    str,
    dict[str, tuple[RecordTransformHandler, ...]],
]:
    return {
        "*": {
            TYRE_MANUFACTURERS_SOURCE: (_tyre_manufacturers_handler,),
        },
        "constructors": {
            DEFAULT_SOURCE_PIPELINE: (_constructor_domain_handler,),
        },
        "constructor": {
            DEFAULT_SOURCE_PIPELINE: (_constructor_domain_handler,),
        },
        "chassis": {
            DEFAULT_SOURCE_PIPELINE: (_constructor_domain_handler,),
        },
        "circuits": {
            DEFAULT_SOURCE_PIPELINE: (_circuits_domain_handler,),
        },
        "engines": {
            DEFAULT_SOURCE_PIPELINE: (_engines_domain_handler,),
        },
        "grands_prix": {
            DEFAULT_SOURCE_PIPELINE: (_grands_prix_domain_handler,),
        },
        "teams": {
            DEFAULT_SOURCE_PIPELINE: (_teams_domain_handler,),
        },
        "drivers": {
            DEFAULT_SOURCE_PIPELINE: (_drivers_domain_handler,),
        },
        "races": {
            DEFAULT_SOURCE_PIPELINE: (_races_domain_handler,),
        },
    }


TRANSFORM_PIPELINES = _build_transform_pipelines()
validate_sources_registry_consistency()


def _resolve_record_transform_handlers(
    domain: str,
    source_name: str,
) -> tuple[RecordTransformHandler, ...]:
    global_handlers = TRANSFORM_PIPELINES.get("*", {})
    domain_handlers = TRANSFORM_PIPELINES.get(domain, {})

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
    classification: SourceClassification,
) -> dict[str, object]:
    if domain not in CHASSIS_CONSTRUCTOR_DOMAINS:
        return transformed

    if classification.has("constructor_indianapolis_only"):
        return _transform_indianapolis_only_constructor(transformed)
    if classification.has("constructor_former"):
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
                "status": "former",
                "indianapolis_only": True,
            },
        },
    }


def _transform_former_constructor(transformed: dict[str, object]) -> dict[str, object]:
    constructor = transformed.get("constructor")
    formula_one = {
        key: value for key, value in transformed.items() if key != "constructor"
    }
    formula_one["status"] = "former"
    return {
        "constructor": constructor,
        "racing_series": _build_racing_series(formula_one),
    }


def _ensure_constructor_status(transformed: dict[str, object]) -> None:
    if "racing_series" not in transformed:
        transformed["status"] = "active"
        transformed["series"] = FORMULA_ONE_SERIES.copy()
        return

    racing_series = transformed.get("racing_series")
    if not isinstance(racing_series, dict):
        racing_series = {}
        transformed["racing_series"] = racing_series
    formula_one = racing_series.setdefault("formula_one", {})
    formula_one.setdefault("status", "active")


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
    classification: SourceClassification,
) -> dict[str, object]:
    if domain != "engines":
        return transformed
    if classification.has("engine_indianapolis_only"):
        transformed["racing_series"] = {
            "AAA_national_championship": [],
            "formula_one": {"status": "former", "indianapolis_only": True},
        }
    elif classification.has("engine_manufacturers"):
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
    classification: SourceClassification,
) -> dict[str, object]:
    if domain != "teams":
        return transformed
    if classification.has("team_constructor_snapshot"):
        transformed = {
            "team": transformed.get("constructor"),
            "racing_series": _build_racing_series({**transformed}),
        }
    if classification.has("team_sponsorship_liveries") and "liveries" in transformed:
        transformed["racing_series"] = _build_racing_series(
            {"liveries": transformed.pop("liveries")},
        )
    if classification.has("team_privateer"):
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
    classification: SourceClassification,
) -> dict[str, object]:
    if domain != "drivers":
        return transformed
    if classification.has("driver_f1"):
        return _transform_f1_driver(transformed)
    if classification.has("driver_female"):
        return _transform_female_driver(transformed)
    if classification.has("driver_fatalities"):
        _attach_driver_death_data(transformed)
    return transformed


def _transform_f1_driver(transformed: dict[str, object]) -> dict[str, object]:
    driver = transformed.pop("driver", None)
    nationality = transformed.pop("nationality", None)
    formula_one = _normalize_driver_series_stats(transformed)
    return {
        "driver": driver,
        "nationality": nationality,
        "racing_series": _build_racing_series(formula_one),
    }


def _transform_female_driver(transformed: dict[str, object]) -> dict[str, object]:
    driver = transformed.pop("driver", None)
    formula_one = _normalize_driver_series_stats(transformed)
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
    classification: SourceClassification,
) -> dict[str, object]:
    if domain != "races":
        return transformed
    if classification.has("race_red_flag_world_championship"):
        transformed["championship"] = True
    if classification.has("race_red_flag_non_championship"):
        transformed["championship"] = False
    transformed["red_flag"] = _extract_red_flag(transformed)
    _pop_red_flag_fields(transformed)
    return transformed


def _iter_transformed_records(
    domain: str,
    source_name: str,
    classification: SourceClassification,
    payload: object,
) -> list[object]:
    if isinstance(payload, list):
        transformed = [
            _transform_record(domain, source_name, classification, item)
            for item in payload
        ]
        if domain == "engines":
            return [
                engine_record.to_dict()
                if (engine_record := EngineRecordModel.from_object(record)) is not None
                else record
                for record in transformed
            ]
        if domain != "races":
            return transformed
        return [
            race_record.to_dict()
            if (race_record := RaceRecordModel.from_object(record)) is not None
            else record
            for record in transformed
        ]

    transformed_record = _transform_record(domain, source_name, classification, payload)
    if domain == "engines":
        engine_record = EngineRecordModel.from_object(transformed_record)
        if engine_record is not None:
            return [engine_record.to_dict()]
    if domain == "races":
        race_record = RaceRecordModel.from_object(transformed_record)
        if race_record is not None:
            return [race_record.to_dict()]
    return [transformed_record]


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


def _iter_mergeable_domain_dirs(layer_zero_dir: Path, resolver: PathResolver) -> list[Path]:
    domain_dirs: list[Path] = []
    for domain_dir in sorted(p for p in layer_zero_dir.iterdir() if p.is_dir()):
        raw_dir = resolver.raw_dir(domain=domain_dir.name)
        if not raw_dir.exists() or not raw_dir.is_dir():
            continue
        if domain_dir.name in {"points", "rules"}:
            continue
        domain_dirs.append(domain_dir)
    return domain_dirs


def _load_domain_records(domain_dir: Path, resolver: PathResolver) -> list[object]:
    merged_records: list[object] = []
    raw_dir = resolver.raw_dir(domain=domain_dir.name)
    for json_path in sorted(raw_dir.rglob("*.json")):
        classification = classify_source(
            SourceMetadata(domain=domain_dir.name, source_name=json_path.name),
        )
        logger.info(
            "Selected processing path for %s/%s: %s",
            domain_dir.name,
            json_path.name,
            classification.describe_path(),
        )
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        merged_records.extend(
            _iter_transformed_records(
                domain_dir.name,
                json_path.name,
                classification,
                payload,
            ),
        )
    return merged_records


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
    """Aktywna, gdy domena to `drivers`."""
    return sorted(items, key=_driver_sort_key)


def _sort_constructors_by_name(items: list[object]) -> list[object]:
    """Aktywna, gdy domena należy do `CHASSIS_CONSTRUCTOR_DOMAINS`."""
    return sorted(items, key=_constructor_sort_key)


def _nest_team_liveries(items: list[object]) -> list[object]:
    """Aktywna, gdy domena to `teams`."""
    return [_nest_team_liveries_in_seasons(record) for record in items]


def _sort_teams_by_name(items: list[object]) -> list[object]:
    """Aktywna, gdy domena to `teams`."""
    return sorted(items, key=_team_sort_key)


def _sort_seasons_by_year(items: list[object]) -> list[object]:
    """Aktywna, gdy domena to `seasons`."""
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


def _post_process_domain_records(domain: str, records: list[object]) -> list[object]:
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


def _write_merged_domain_records(
    domain_dir: Path,
    merged_records: list[object],
    resolver: PathResolver,
) -> None:
    merged_path = resolver.merged(domain=domain_dir.name)
    merged_path.write_text(
        json.dumps(merged_records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
