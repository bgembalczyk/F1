import re
from collections.abc import Callable

from layers.zero.merge_types import EngineRecordModel
from layers.zero.merge_types import RaceRecordModel
from scrapers.wiki.constants import CHASSIS_CONSTRUCTOR_DOMAINS
from scrapers.wiki.constants import CIRCUITS_FORMULA_ONE_FIELDS
from scrapers.wiki.constants import CONSTRUCTORS_FORMULA_ONE_FIELDS
from scrapers.wiki.constants import ENGINES_FORMULA_ONE_FIELDS
from scrapers.wiki.constants import FORMULA_ONE_SERIES
from scrapers.wiki.constants import GRANDS_PRIX_FORMULA_ONE_FIELDS
from scrapers.wiki.constants import RED_FLAG_FIELDS
from scrapers.wiki.sources_registry import FORMER_CONSTRUCTORS_SOURCE
from scrapers.wiki.sources_registry import INDIANAPOLIS_ONLY_CONSTRUCTORS_SOURCE
from scrapers.wiki.sources_registry import TYRE_MANUFACTURERS_SOURCE
from scrapers.wiki.sources_registry import validate_sources_registry_consistency

RecordTransformHandler = Callable[
    [str, str, dict[str, object]],
    dict[str, object],
]
DEFAULT_SOURCE_PIPELINE = "*"


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


def _transform_record(domain: str, source_name: str, record: object) -> object:
    if not isinstance(record, dict):
        return record

    transformed = dict(record)
    for handler in _resolve_record_transform_handlers(domain, source_name):
        transformed = handler(domain, source_name, transformed)
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
) -> dict[str, object]:
    if domain != "engines":
        return transformed
    if source_name == "f1_indianapolis_only_engine_manufacturers.json":
        transformed["racing_series"] = {
            "AAA_national_championship": [],
            "formula_one": {"status": "former", "indianapolis_only": True},
        }
    elif source_name == "f1_engine_manufacturers.json":
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
    if source_name == "f1_sponsorship_liveries.json" and "liveries" in transformed:
        transformed["racing_series"] = _build_racing_series(
            {"liveries": transformed.pop("liveries")},
        )
    if source_name == "f1_privateer_teams.json":
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
    if source_name == "f1_drivers.json":
        return _transform_f1_driver(transformed)
    if source_name == "female_drivers.json":
        return _transform_female_driver(transformed)
    if source_name == "f1_driver_fatalities.json":
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
) -> dict[str, object]:
    if domain != "races":
        return transformed
    if source_name == "f1_red_flagged_world_championship_races.json":
        transformed["championship"] = True
    if source_name == "f1_red_flagged_non_championship_races.json":
        transformed["championship"] = False
    transformed["red_flag"] = _extract_red_flag(transformed)
    _pop_red_flag_fields(transformed)
    return transformed


def _iter_transformed_records(
    domain: str,
    source_name: str,
    payload: object,
) -> list[object]:
    if isinstance(payload, list):
        transformed = [_transform_record(domain, source_name, item) for item in payload]
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

    transformed_record = _transform_record(domain, source_name, payload)
    if domain == "engines":
        engine_record = EngineRecordModel.from_object(transformed_record)
        if engine_record is not None:
            return [engine_record.to_dict()]
    if domain == "races":
        race_record = RaceRecordModel.from_object(transformed_record)
        if race_record is not None:
            return [race_record.to_dict()]
    return [transformed_record]
