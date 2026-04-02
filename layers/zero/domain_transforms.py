from __future__ import annotations

import re
from collections.abc import Callable

from layers.zero.merge_types import DriverRecordModel
from layers.zero.merge_types import DriverSeriesStats
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

RecordTransformHandler = Callable[[str, str, dict[str, object]], dict[str, object]]

DEFAULT_SOURCE_PIPELINE = "*"


def build_domain_transformers() -> dict[str, dict[str, tuple[RecordTransformHandler, ...]]]:
    return {
        "*": {TYRE_MANUFACTURERS_SOURCE: (_tyre_manufacturers_handler,)},
        "constructors": {DEFAULT_SOURCE_PIPELINE: (_constructor_domain_handler,)},
        "constructor": {DEFAULT_SOURCE_PIPELINE: (_constructor_domain_handler,)},
        "chassis": {DEFAULT_SOURCE_PIPELINE: (_constructor_domain_handler,)},
        "circuits": {DEFAULT_SOURCE_PIPELINE: (_circuits_domain_handler,)},
        "engines": {DEFAULT_SOURCE_PIPELINE: (_engines_domain_handler,)},
        "grands_prix": {DEFAULT_SOURCE_PIPELINE: (_grands_prix_domain_handler,)},
        "teams": {DEFAULT_SOURCE_PIPELINE: (_teams_domain_handler,)},
        "drivers": {DEFAULT_SOURCE_PIPELINE: (_drivers_domain_handler,)},
        "races": {DEFAULT_SOURCE_PIPELINE: (_races_domain_handler,)},
    }


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


def normalize_driver_stats(incoming: dict[str, object]) -> dict[str, object]:
    return DriverSeriesStats.from_dict(incoming).to_dict()


def _build_racing_series(formula_one: dict[str, object]) -> dict[str, object]:
    return {"formula_one": formula_one}


def _move_fields_to_formula_one(transformed: dict[str, object], fields: set[str]) -> None:
    formula_one = {key: transformed.pop(key) for key in fields if key in transformed}
    if not formula_one:
        return
    transformed["racing_series"] = _build_racing_series(formula_one)


def _extract_red_flag(record: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in record.items() if key in RED_FLAG_FIELDS}


def _pop_red_flag_fields(record: dict[str, object]) -> None:
    for key in RED_FLAG_FIELDS:
        record.pop(key, None)


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

    source_strategy = {
        INDIANAPOLIS_ONLY_CONSTRUCTORS_SOURCE: _transform_indianapolis_only_constructor,
        FORMER_CONSTRUCTORS_SOURCE: _transform_former_constructor,
    }
    strategy = source_strategy.get(source_name)
    if strategy is not None:
        return strategy(transformed)

    constructor_fields = set(CONSTRUCTORS_FORMULA_ONE_FIELDS)
    if domain == "constructors" and re.fullmatch(r"f1_constructors_\d{4}\.json", source_name):
        constructor_fields.discard("engine")

    _move_fields_to_formula_one(transformed, constructor_fields)
    _ensure_constructor_status(transformed)
    return transformed


def _transform_indianapolis_only_constructor(transformed: dict[str, object]) -> dict[str, object]:
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


def _transform_circuits_domain(domain: str, transformed: dict[str, object]) -> dict[str, object]:
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

    source_strategy: dict[str, Callable[[dict[str, object]], dict[str, object]]] = {
        "f1_indianapolis_only_engine_manufacturers.json": _set_indianapolis_engine_series,
        "f1_engine_manufacturers.json": _move_engine_formula_one_fields,
    }
    strategy = source_strategy.get(source_name)
    if strategy is None:
        return transformed
    return strategy(transformed)


def _set_indianapolis_engine_series(transformed: dict[str, object]) -> dict[str, object]:
    transformed["racing_series"] = {
        "AAA_national_championship": [],
        "formula_one": {"status": "former", "indianapolis_only": True},
    }
    return transformed


def _move_engine_formula_one_fields(transformed: dict[str, object]) -> dict[str, object]:
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

    def _constructors_yearly(team_record: dict[str, object]) -> dict[str, object]:
        return {
            "team": team_record.get("constructor"),
            "racing_series": _build_racing_series({**team_record}),
        }

    def _sponsorship_liveries(team_record: dict[str, object]) -> dict[str, object]:
        if "liveries" in team_record:
            team_record["racing_series"] = _build_racing_series(
                {"liveries": team_record.pop("liveries")},
            )
        return team_record

    def _privateer(team_record: dict[str, object]) -> dict[str, object]:
        formula_one = {key: team_record.pop(key) for key in ("seasons",) if key in team_record}
        formula_one["privateer"] = True
        team_record["racing_series"] = _build_racing_series(formula_one)
        return team_record

    source_strategy: dict[str, Callable[[dict[str, object]], dict[str, object]]] = {
        "f1_sponsorship_liveries.json": _sponsorship_liveries,
        "f1_privateer_teams.json": _privateer,
    }
    strategy = source_strategy.get(source_name)
    if strategy is not None:
        return strategy(transformed)

    if re.fullmatch(r"f1_constructors_\d{4}\.json", source_name):
        return _constructors_yearly(transformed)
    return transformed


def _transform_drivers_domain(
    domain: str,
    source_name: str,
    transformed: dict[str, object],
) -> dict[str, object]:
    if domain != "drivers":
        return transformed

    source_strategy: dict[str, Callable[[dict[str, object]], dict[str, object]]] = {
        "f1_drivers.json": _transform_f1_driver,
        "female_drivers.json": _transform_female_driver,
        "f1_driver_fatalities.json": _transform_driver_fatality,
    }
    strategy = source_strategy.get(source_name)
    if strategy is None:
        return transformed
    return strategy(transformed)


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


def _transform_driver_fatality(transformed: dict[str, object]) -> dict[str, object]:
    death_fields = {key: transformed.pop(key) for key in ("date", "age") if key in transformed}
    crash_fields = {
        key: transformed.pop(key)
        for key in ("event", "circuit", "car", "session")
        if key in transformed
    }
    transformed["death"] = {**death_fields, "crash": crash_fields}
    return transformed


def _transform_races_domain(
    domain: str,
    source_name: str,
    transformed: dict[str, object],
) -> dict[str, object]:
    if domain != "races":
        return transformed

    championship_by_source = {
        "f1_red_flagged_world_championship_races.json": True,
        "f1_red_flagged_non_championship_races.json": False,
    }
    championship = championship_by_source.get(source_name)
    if championship is not None:
        transformed["championship"] = championship

    transformed["red_flag"] = _extract_red_flag(transformed)
    _pop_red_flag_fields(transformed)
    return transformed
