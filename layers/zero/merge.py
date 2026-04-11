import logging
import re
from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

from layers.orchestration.constants import CONSTRUCTOR_STATUS_ACTIVE
from layers.orchestration.constants import CONSTRUCTOR_STATUS_FORMER
from layers.path_resolver import PathResolver
from layers.zero.domain_postprocess import configure_domain_postprocessors
from layers.zero.domain_postprocess import post_process_domain_records
from layers.zero.record_merge_ops import merge_driver_values
from layers.zero.record_merge_ops import merge_duplicate_records
from layers.zero.source_routing import iter_mergeable_domain_dirs
from layers.zero.source_routing import load_domain_records
from layers.zero.source_routing import write_merged_domain_records
from models.merge_types.link_value import LinkValue
from models.merge_types.record.driver import DriverRecordModel
from models.merge_types.record.engine import EngineRecordModel
from models.merge_types.record.race import RaceRecordModel
from scrapers import constants_wiki
from scrapers import sources_registry_wiki as sources_registry
from scrapers.constants_wiki import CHASSIS_CONSTRUCTOR_DOMAINS
from scrapers.constants_wiki import CIRCUITS_FORMULA_ONE_FIELDS
from scrapers.constants_wiki import CONSTRUCTORS_FORMULA_ONE_FIELDS
from scrapers.constants_wiki import ENGINES_FORMULA_ONE_FIELDS
from scrapers.constants_wiki import FORMULA_ONE_SERIES
from scrapers.constants_wiki import GRANDS_PRIX_FORMULA_ONE_FIELDS
from scrapers.constants_wiki import RED_FLAG_FIELDS

RecordTransformHandler = Callable[
    [str, str, dict[str, object]],
    dict[str, object],
]
DomainRecordsProcessor = Callable[[list[object]], list[object]]

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DomainPipelineConfig:
    transformers: dict[str, tuple[RecordTransformHandler, ...]] = field(
        default_factory=dict,
    )
    postprocessors: tuple[tuple[str, DomainRecordsProcessor], ...] = ()
    records_normalizer: DomainRecordsProcessor | None = None


def build_racing_series(formula_one: dict[str, object]) -> dict[str, object]:
    sorted_formula_one = {key: formula_one[key] for key in sorted(formula_one)}
    return {"formula_one": sorted_formula_one}


def move_fields_to_formula_one(
    transformed: dict[str, object],
    fields: set[str],
) -> None:
    formula_one = {key: transformed.pop(key) for key in fields if key in transformed}
    if not formula_one:
        return
    transformed["racing_series"] = build_racing_series(formula_one)


def link_text(value: object) -> str:
    if (link := LinkValue.from_object(value)) is not None:
        return link.text
    return str(value or "")


def normalized_text(value: object) -> str:
    return link_text(value).strip().casefold()


def sort_key_with_presence(value: object) -> tuple[int, str]:
    text = normalized_text(value)
    return (0, text) if text else (1, "")


def extract_red_flag(record: dict[str, object]) -> dict[str, object]:
    return {
        key: value for key, value in record.items() if key in RED_FLAG_FIELDS
    }


def pop_red_flag_fields(record: dict[str, object]) -> None:
    for key in RED_FLAG_FIELDS:
        record.pop(key, None)


def transform_record(domain: str, source_name: str, record: object) -> object:
    if not isinstance(record, dict):
        return record

    canonical_source_name = sources_registry.resolve_list_filename(source_name)
    transformed = dict(record)
    for handler in resolve_record_transform_handlers(domain, canonical_source_name):
        transformed = handler(domain, canonical_source_name, transformed)
    return transformed


def tyre_manufacturers_handler(
    domain: str,
    source_name: str,
    record: dict[str, object],
) -> dict[str, object]:
    _ = domain
    return transform_tyre_manufacturers(source_name, record)


def constructor_domain_handler(
    domain: str,
    source_name: str,
    record: dict[str, object],
) -> dict[str, object]:
    return transform_constructor_domain(domain, source_name, record)


def circuits_domain_handler(
    domain: str,
    source_name: str,
    record: dict[str, object],
) -> dict[str, object]:
    _ = source_name
    return transform_circuits_domain(domain, record)


def engines_domain_handler(
    domain: str,
    source_name: str,
    record: dict[str, object],
) -> dict[str, object]:
    return transform_engines_domain(domain, source_name, record)


def grands_prix_domain_handler(
    domain: str,
    source_name: str,
    record: dict[str, object],
) -> dict[str, object]:
    _ = source_name
    return transform_grands_prix_domain(domain, record)


def teams_domain_handler(
    domain: str,
    source_name: str,
    record: dict[str, object],
) -> dict[str, object]:
    return transform_teams_domain(domain, source_name, record)


def drivers_domain_handler(
    domain: str,
    source_name: str,
    record: dict[str, object],
) -> dict[str, object]:
    return transform_drivers_domain(domain, source_name, record)


def races_domain_handler(
    domain: str,
    source_name: str,
    record: dict[str, object],
) -> dict[str, object]:
    return transform_races_domain(domain, source_name, record)


DEFAULT_SOURCE_PIPELINE = "*"
ENGINE_REGULATIONS_SOURCE = sources_registry.get_source_by_seed_name(
    "engines_regulations",
    warn=False,
).list_filename
ENGINE_RESTRICTIONS_SOURCE = sources_registry.get_source_by_seed_name(
    "engines_restrictions",
    warn=False,
).list_filename
POINTS_SCORING_SYSTEM_SOURCE = sources_registry.get_source_by_seed_name(
    "points_history",
    warn=False,
).list_filename
POINTS_SCORING_SYSTEM_SHORTENED_SOURCE = sources_registry.get_source_by_seed_name(
    "points_shortened",
    warn=False,
).list_filename
POINTS_SCORING_SYSTEM_SPRINT_SOURCE = sources_registry.get_source_by_seed_name(
    "points_sprint",
    warn=False,
).list_filename


def normalize_engine_records(records: list[object]) -> list[object]:
    return [
        engine_record.to_dict()
        if (engine_record := EngineRecordModel.from_object(record)) is not None
        else record
        for record in records
    ]


def normalize_race_records(records: list[object]) -> list[object]:
    return [
        race_record.to_dict()
        if (race_record := RaceRecordModel.from_object(record)) is not None
        else record
        for record in records
    ]


DOMAIN_PIPELINE_CONFIGS: dict[str, DomainPipelineConfig] = {
    "*": DomainPipelineConfig(
        transformers={
            sources_registry.TYRE_MANUFACTURERS_SOURCE: (tyre_manufacturers_handler,),
        },
    ),
    "constructors": DomainPipelineConfig(
        transformers={DEFAULT_SOURCE_PIPELINE: (constructor_domain_handler,)},
    ),
    "constructor": DomainPipelineConfig(
        transformers={DEFAULT_SOURCE_PIPELINE: (constructor_domain_handler,)},
    ),
    "chassis": DomainPipelineConfig(
        transformers={DEFAULT_SOURCE_PIPELINE: (constructor_domain_handler,)},
    ),
    "chassis_constructors": DomainPipelineConfig(
        transformers={DEFAULT_SOURCE_PIPELINE: (constructor_domain_handler,)},
    ),
    "circuits": DomainPipelineConfig(
        transformers={DEFAULT_SOURCE_PIPELINE: (circuits_domain_handler,)},
    ),
    "engines": DomainPipelineConfig(
        transformers={DEFAULT_SOURCE_PIPELINE: (engines_domain_handler,)},
        records_normalizer=normalize_engine_records,
    ),
    "grands_prix": DomainPipelineConfig(
        transformers={DEFAULT_SOURCE_PIPELINE: (grands_prix_domain_handler,)},
    ),
    "teams": DomainPipelineConfig(
        transformers={DEFAULT_SOURCE_PIPELINE: (teams_domain_handler,)},
    ),
    "drivers": DomainPipelineConfig(
        transformers={DEFAULT_SOURCE_PIPELINE: (drivers_domain_handler,)},
    ),
    "races": DomainPipelineConfig(
        transformers={DEFAULT_SOURCE_PIPELINE: (races_domain_handler,)},
        records_normalizer=normalize_race_records,
    ),
}

sources_registry.validate_sources_registry_consistency()


def resolve_record_transform_handlers(
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


def transform_tyre_manufacturers(
    source_name: str,
    transformed: dict[str, object],
) -> dict[str, object]:
    if source_name != sources_registry.TYRE_MANUFACTURERS_SOURCE:
        return transformed

    if "manufacturers" in transformed:
        transformed["tyre_manufacturers"] = transformed.pop("manufacturers")
    seasons = transformed.get("seasons")
    if isinstance(seasons, list) and len(seasons) == 1:
        transformed["season"] = transformed.pop("seasons")[0]
    return transformed


def transform_constructor_domain(
    domain: str,
    source_name: str,
    transformed: dict[str, object],
) -> dict[str, object]:
    constructor_domains = CHASSIS_CONSTRUCTOR_DOMAINS | {
        "constructor",
        "chassis",
    }
    if domain not in constructor_domains:
        return transformed

    if source_name == sources_registry.INDIANAPOLIS_ONLY_CONSTRUCTORS_SOURCE:
        return transform_indianapolis_only_constructor(transformed)
    if source_name == sources_registry.FORMER_CONSTRUCTORS_SOURCE:
        return transform_former_constructor(domain, transformed)
    if domain in {"chassis_constructors", "chassis", "constructor"} and re.fullmatch(
        r"f1_constructors_\d{4}\.json",
        source_name,
    ):
        return transform_chassis_constructor_from_current_constructors(transformed)

    constructor_fields = set(CONSTRUCTORS_FORMULA_ONE_FIELDS)
    if domain == "constructors" and re.fullmatch(
        r"f1_constructors_\d{4}\.json",
        source_name,
    ):
        constructor_fields.discard("engine")

    move_fields_to_formula_one(transformed, constructor_fields)
    ensure_constructor_status(transformed)
    return transformed


def transform_chassis_constructor_from_current_constructors(
    transformed: dict[str, object],
) -> dict[str, object]:
    constructor_value = transformed.get("constructor")
    if not isinstance(constructor_value, dict):
        return transformed

    chassis_constructor = constructor_value.get("chassis_constructor")
    reshaped: dict[str, object] = {}
    if chassis_constructor is not None:
        reshaped["chassis_constructor"] = chassis_constructor

    for key, value in transformed.items():
        if key == "constructor":
            continue
        reshaped[key] = value

    engine_constructor = constructor_value.get("engine_constructor")
    if engine_constructor is not None:
        reshaped["engine_constructors"] = (
            engine_constructor
            if isinstance(engine_constructor, list)
            else [engine_constructor]
        )

    return reshaped


def transform_indianapolis_only_constructor(
    transformed: dict[str, object],
) -> dict[str, object]:
    constructor_key = "constructor"
    constructor_value: object = {
        "text": transformed.get("constructor"),
        "url": transformed.get("constructor_url"),
    }

    chassis_constructor = transformed.get("chassis_constructor")
    if isinstance(chassis_constructor, dict):
        constructor_key = "chassis_constructor"
        constructor_value = chassis_constructor

    return {
        constructor_key: constructor_value,
        "racing_series": {
            "AAA_national_championship": [],
            "formula_one": {
                "status": CONSTRUCTOR_STATUS_FORMER,
                "indianapolis_only": True,
            },
        },
    }


def transform_former_constructor(
    domain: str,
    transformed: dict[str, object],
) -> dict[str, object]:
    if domain in {"chassis_constructors", "chassis", "constructor"}:
        flattened = {
            key: value for key, value in transformed.items() if key != "constructor"
        }
        flattened["status"] = CONSTRUCTOR_STATUS_FORMER
        return flattened

    constructor = transformed.get("constructor")
    formula_one = {
        key: value for key, value in transformed.items() if key != "constructor"
    }
    formula_one["status"] = CONSTRUCTOR_STATUS_FORMER
    return {
        "constructor": constructor,
        "racing_series": build_racing_series(formula_one),
    }


def ensure_constructor_status(transformed: dict[str, object]) -> None:
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


def transform_circuits_domain(
    domain: str,
    transformed: dict[str, object],
) -> dict[str, object]:
    if domain != "circuits":
        return transformed
    move_fields_to_formula_one(transformed, CIRCUITS_FORMULA_ONE_FIELDS)
    if "racing_series" not in transformed:
        transformed["series"] = FORMULA_ONE_SERIES.copy()
    return transformed


def transform_engines_domain(
    domain: str,
    source_name: str,
    transformed: dict[str, object],
) -> dict[str, object]:
    if domain != "engines":
        return transformed

    if "engine_constructor" not in transformed:
        if "manufacturer" in transformed:
            transformed["engine_constructor"] = transformed.pop("manufacturer")
        elif "engine_manufacturer" in transformed:
            transformed["engine_constructor"] = transformed.pop("engine_manufacturer")

    if source_name in (
        sources_registry.INDIANAPOLIS_ONLY_ENGINES_SOURCE,
        sources_registry.ENGINE_MANUFACTURERS_INDIANAPOLIS_ONLY_SOURCE,
    ):
        transformed["racing_series"] = {
            "AAA_national_championship": [],
            "formula_one": {
                "status": CONSTRUCTOR_STATUS_FORMER,
                "indianapolis_only": True,
            },
        }
    elif source_name == sources_registry.ENGINE_MANUFACTURERS_SOURCE:
        move_fields_to_formula_one(transformed, ENGINES_FORMULA_ONE_FIELDS)
    return transformed


def transform_grands_prix_domain(
    domain: str,
    transformed: dict[str, object],
) -> dict[str, object]:
    if domain == "grands_prix":
        move_fields_to_formula_one(
            transformed,
            GRANDS_PRIX_FORMULA_ONE_FIELDS,
        )
    return transformed


def transform_teams_domain(
    domain: str,
    source_name: str,
    transformed: dict[str, object],
) -> dict[str, object]:
    if domain != "teams":
        return transformed
    if re.fullmatch(r"f1_constructors_\d{4}\.json", source_name):
        transformed = transform_teams_from_current_constructors(transformed)
    if (
        source_name == sources_registry.SPONSORSHIP_LIVERIES_SOURCE
        and "liveries" in transformed
    ):
        transformed["racing_series"] = build_racing_series(
            {"liveries": transformed.pop("liveries")},
        )
    if source_name == sources_registry.PRIVATEER_TEAMS_SOURCE:
        formula_one = {
            key: transformed.pop(key) for key in ("seasons",) if key in transformed
        }
        formula_one["privateer"] = True
        transformed["racing_series"] = build_racing_series(formula_one)
    return transformed


def transform_teams_from_current_constructors(
    transformed: dict[str, object],
) -> dict[str, object]:
    constructor_value = transformed.get("constructor")
    if not (
        isinstance(constructor_value, dict)
        and "chassis_constructor" in constructor_value
    ):
        return {
            "team": constructor_value,
            "racing_series": build_racing_series({**transformed}),
        }

    team_value: object = constructor_value["chassis_constructor"]
    constructors: list[dict[str, object]] = []

    constructor_entry: dict[str, object] = {
        "chassis_constructor": constructor_value["chassis_constructor"],
    }
    engine_constructor = constructor_value.get("engine_constructor")
    if engine_constructor is not None:
        constructor_entry["engine_constructor"] = engine_constructor
    constructors.append(constructor_entry)

    formula_one = {
        key: value for key, value in transformed.items() if key != "constructor"
    }
    if constructors:
        formula_one["constructors"] = constructors
    return {
        "team": team_value,
        "racing_series": build_racing_series(formula_one),
    }


def transform_drivers_domain(
    domain: str,
    source_name: str,
    transformed: dict[str, object],
) -> dict[str, object]:
    if domain != "drivers":
        return transformed
    normalize_driver_entry_start_fields(transformed)
    if source_name == sources_registry.DRIVERS_SOURCE:
        return transform_f1_driver(transformed)
    if source_name == sources_registry.FEMALE_DRIVERS_SOURCE:
        return transform_female_driver(transformed)
    if source_name == sources_registry.DRIVER_FATALITIES_SOURCE:
        attach_driver_death_data(transformed)
    return transformed


def normalize_driver_entry_start_fields(transformed: dict[str, object]) -> None:
    if "race_entries" not in transformed and "entries" in transformed:
        transformed["race_entries"] = transformed.pop("entries")
    else:
        transformed.pop("entries", None)

    if "race_starts" not in transformed and "starts" in transformed:
        transformed["race_starts"] = transformed.pop("starts")
    else:
        transformed.pop("starts", None)


def transform_f1_driver(transformed: dict[str, object]) -> dict[str, object]:
    driver_record = DriverRecordModel(raw=transformed)
    driver, nationality = driver_record.extract_identity()
    formula_one = driver_record.extract_series_stats().to_dict()
    return {
        "driver": driver,
        "nationality": nationality,
        "racing_series": build_racing_series(formula_one),
    }


def transform_female_driver(transformed: dict[str, object]) -> dict[str, object]:
    driver_record = DriverRecordModel(raw=transformed)
    driver, _ = driver_record.extract_identity()
    formula_one = driver_record.extract_series_stats().to_dict()
    return {
        "driver": driver,
        "gender": "female",
        "racing_series": build_racing_series(formula_one),
    }


def attach_driver_death_data(transformed: dict[str, object]) -> None:
    death_fields = {
        key: transformed.pop(key) for key in ("date", "age") if key in transformed
    }
    crash_fields = {
        key: transformed.pop(key)
        for key in ("event", "circuit", "car", "session")
        if key in transformed
    }
    transformed["death"] = {**death_fields, "crash": crash_fields}


def transform_races_domain(
    domain: str,
    source_name: str,
    transformed: dict[str, object],
) -> dict[str, object]:
    if domain != "races":
        return transformed
    if source_name == sources_registry.RED_FLAGGED_WORLD_CHAMPIONSHIP_SOURCE:
        transformed["championship"] = True
    if source_name == sources_registry.RED_FLAGGED_NON_CHAMPIONSHIP_SOURCE:
        transformed["championship"] = False
    transformed["red_flag"] = extract_red_flag(transformed)
    pop_red_flag_fields(transformed)
    return transformed


def iter_transformed_records(
    domain: str,
    source_name: str,
    payload: object,
) -> list[object]:
    domain_config = DOMAIN_PIPELINE_CONFIGS.get(domain, DomainPipelineConfig())

    if isinstance(payload, list):
        transformed: list[object] = []
        for item in payload:
            transformed_record = transform_record(domain, source_name, item)
            transformed.extend(
                expand_season_records(
                    domain=domain,
                    source_name=source_name,
                    record=transformed_record,
                ),
            )
        if domain_config.records_normalizer is None:
            return transformed
        return domain_config.records_normalizer(transformed)

    transformed_record = transform_record(domain, source_name, payload)
    records = expand_season_records(
        domain=domain,
        source_name=source_name,
        record=transformed_record,
    )
    if domain_config.records_normalizer is None:
        return records
    return domain_config.records_normalizer(records)


def season_payload_key(source_name: str) -> str | None:
    if source_name == ENGINE_REGULATIONS_SOURCE:
        return "engine_regulations"
    if source_name == ENGINE_RESTRICTIONS_SOURCE:
        return "engine_restrictions"
    if source_name == POINTS_SCORING_SYSTEM_SOURCE:
        return "points_scoring_system"
    if source_name == POINTS_SCORING_SYSTEM_SHORTENED_SOURCE:
        return "points_scoring_system_shortened"
    if source_name == POINTS_SCORING_SYSTEM_SPRINT_SOURCE:
        return "points_scoring_system_sprint"
    return None


def expand_season_records(
    *,
    domain: str,
    source_name: str,
    record: object,
) -> list[object]:
    if domain not in {"season", "seasons"} or not isinstance(record, dict):
        return [record]

    payload_key = season_payload_key(source_name)
    is_tyre_source = source_name == sources_registry.TYRE_MANUFACTURERS_SOURCE
    if not is_tyre_source and payload_key is None:
        return [record]

    transformed = dict(record)
    if is_tyre_source and "manufacturers" in transformed:
        transformed["tyre_manufacturers"] = transformed.pop("manufacturers")
    if source_name == ENGINE_RESTRICTIONS_SOURCE and "seasons" not in transformed:
        restriction_years = transformed.pop("year", None)
        if isinstance(restriction_years, list):
            transformed["seasons"] = restriction_years

    seasons = transformed.pop("seasons", None)
    if not isinstance(seasons, list) or not seasons:
        return [transformed]

    if payload_key is None:
        payload_fields = dict(transformed)
    else:
        payload_fields = {payload_key: transformed}

    return [{"season": season, **payload_fields} for season in seasons]


def merge_duplicate_drivers(records: list[object]) -> list[object]:
    """Aktywna, gdy domena to `drivers`."""
    return merge_duplicate_records(records, DriverRecordModel, merge_driver_values)


configure_domain_postprocessors(DOMAIN_PIPELINE_CONFIGS, DomainPipelineConfig)


def _post_process_domain_records(domain: str, records: list[object]) -> list[object]:
    return post_process_domain_records(
        domain=domain,
        records=records,
        domain_pipeline_configs=DOMAIN_PIPELINE_CONFIGS,
        domain_pipeline_config_factory=DomainPipelineConfig,
    )


def merge_layer_zero_raw_outputs(base_wiki_dir: Path) -> None:
    layer_zero_dir = base_wiki_dir / "layers" / "0_layer"
    if not layer_zero_dir.exists():
        return

    resolver = PathResolver(layer_zero_root=layer_zero_dir)

    for domain_dir in iter_mergeable_domain_dirs(layer_zero_dir, resolver):
        merged_records = load_domain_records(
            domain_dir,
            resolver,
            transform_records=iter_transformed_records,
        )
        if not merged_records:
            continue
        merged_records = _post_process_domain_records(domain_dir.name, merged_records)
        write_merged_domain_records(domain_dir, merged_records, resolver)
