from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Any

import pytest

from models.mappers.field_aliases import FIELD_ALIASES
from models.mappers.field_aliases import apply_field_aliases
from models.records.factories import build_circuit_record
from models.records.factories import build_constructor_record
from models.records.factories import build_driver_record
from models.records.factories import build_engine_manufacturer_record
from models.records.factories import build_fatality_record
from models.records.factories import build_grands_prix_record
from models.records.factories import build_season_summary_record
from models.records.factories import build_special_driver_record
from models.records.factories.car_factory import CarRecordFactory
from models.records.factories.drivers_championships_factory import (
    DriversChampionshipsRecordFactory,
)
from models.records.factories.event_factory import EventRecordFactory
from models.records.factories.helpers import (
    normalize_optional_link_list_or_link_or_string,
)
from models.records.factories.helpers import normalize_optional_link_or_string
from models.records.factories.helpers import normalize_points
from models.records.field_normalizer import FieldNormalizer

NORMALIZER = FieldNormalizer()


def _legacy_driver(record: Mapping[str, Any]) -> dict[str, Any]:
    payload = apply_field_aliases(record, FIELD_ALIASES["driver"], record_name="driver")
    payload["driver"] = NORMALIZER.normalize_link(payload.get("driver"), "driver")
    payload["nationality"] = NORMALIZER.normalize_string(payload.get("nationality"))
    payload["seasons_competed"] = NORMALIZER.normalize_seasons(
        payload.get("seasons_competed"),
    )
    championships = payload.get("drivers_championships") or {}
    if isinstance(championships, Mapping):
        payload["drivers_championships"] = DriversChampionshipsRecordFactory(
            NORMALIZER,
        ).build(championships)
    payload["is_active"] = NORMALIZER.normalize_bool(payload.get("is_active"))
    payload["is_world_champion"] = NORMALIZER.normalize_bool(
        payload.get("is_world_champion"),
    )
    for name in [
        "race_entries",
        "race_starts",
        "pole_positions",
        "race_wins",
        "podiums",
        "fastest_laps",
    ]:
        payload[name] = NORMALIZER.normalize_int(payload.get(name), name)
    payload.setdefault("drivers_championships", {"count": 0, "seasons": []})
    payload.setdefault("seasons_competed", [])
    return payload


def _legacy_constructor(record: Mapping[str, Any]) -> dict[str, Any]:
    payload = apply_field_aliases(
        record,
        FIELD_ALIASES["constructor"],
        record_name="constructor",
    )
    payload["constructor"] = NORMALIZER.normalize_link(
        payload.get("constructor"),
        "constructor",
    )
    for name in ["engine", "based_in", "antecedent_teams"]:
        payload[name] = NORMALIZER.normalize_link_list(payload.get(name), name)
    payload["seasons"] = NORMALIZER.normalize_seasons(payload.get("seasons"))
    payload["licensed_in"] = normalize_optional_link_list_or_link_or_string(
        NORMALIZER,
        payload.get("licensed_in"),
        "licensed_in",
    )
    for name in [
        "races_entered",
        "races_started",
        "drivers",
        "total_entries",
        "wins",
        "points",
        "poles",
        "fastest_laps",
        "podiums",
        "wcc_titles",
        "wdc_titles",
    ]:
        payload[name] = NORMALIZER.normalize_int(payload.get(name), name)
    for key in ["engine", "based_in", "seasons", "antecedent_teams"]:
        payload.setdefault(key, [])
    return payload


def _legacy_circuit(record: Mapping[str, Any]) -> dict[str, Any]:
    payload = dict(record)
    payload["circuit"] = NORMALIZER.normalize_link(payload.get("circuit"), "circuit")
    payload["circuit_status"] = NORMALIZER.normalize_status(
        payload.get("circuit_status"),
        ["current", "future", "former"],
        "circuit_status",
    )
    payload["last_length_used_km"] = NORMALIZER.normalize_float(
        payload.get("last_length_used_km"),
        "last_length_used_km",
    )
    payload["last_length_used_mi"] = NORMALIZER.normalize_float(
        payload.get("last_length_used_mi"),
        "last_length_used_mi",
    )
    payload["turns"] = NORMALIZER.normalize_int(payload.get("turns"), "turns")
    payload["grands_prix_held"] = NORMALIZER.normalize_int(
        payload.get("grands_prix_held"),
        "grands_prix_held",
    )
    payload["grands_prix"] = NORMALIZER.normalize_link_list(
        payload.get("grands_prix"),
        "grands_prix",
    )
    payload["seasons"] = NORMALIZER.normalize_seasons(payload.get("seasons"))
    payload["country"] = normalize_optional_link_or_string(
        NORMALIZER,
        payload.get("country"),
        "country",
    )
    payload.setdefault("grands_prix", [])
    payload.setdefault("seasons", [])
    return payload


def _legacy_special_driver(record: Mapping[str, Any]) -> dict[str, Any]:
    payload = dict(record)
    payload["driver"] = NORMALIZER.normalize_link(payload.get("driver"), "driver")
    payload["seasons"] = NORMALIZER.normalize_seasons(payload.get("seasons"))
    payload["teams"] = NORMALIZER.normalize_link_list(payload.get("teams"), "teams")
    payload["entries"] = NORMALIZER.normalize_int(payload.get("entries"), "entries")
    payload["starts"] = NORMALIZER.normalize_int(payload.get("starts"), "starts")
    payload["points"] = normalize_points(NORMALIZER, payload.get("points"))
    payload.setdefault("seasons", [])
    payload.setdefault("teams", [])
    return payload


def _legacy_grands_prix(record: Mapping[str, Any]) -> dict[str, Any]:
    payload = dict(record)
    payload["race_title"] = NORMALIZER.normalize_link(
        payload.get("race_title"),
        "race_title",
    )
    payload["race_status"] = NORMALIZER.normalize_string(payload.get("race_status"))
    payload["years_held"] = NORMALIZER.normalize_seasons(payload.get("years_held"))
    payload["country"] = NORMALIZER.normalize_link_list(
        payload.get("country"),
        "country",
    )
    payload["circuits"] = NORMALIZER.normalize_int(payload.get("circuits"), "circuits")
    payload["total"] = NORMALIZER.normalize_int(payload.get("total"), "total")
    payload.setdefault("years_held", [])
    payload.setdefault("country", [])
    return payload


def _legacy_fatality(record: Mapping[str, Any]) -> dict[str, Any]:
    payload = dict(record)
    payload["driver"] = NORMALIZER.normalize_link(payload.get("driver"), "driver")
    payload["circuit"] = NORMALIZER.normalize_link(payload.get("circuit"), "circuit")
    payload["age"] = NORMALIZER.normalize_int(payload.get("age"), "age")
    event = payload.get("event")
    payload["event"] = (
        EventRecordFactory(NORMALIZER).build(event)
        if isinstance(event, Mapping)
        else None
    )
    car = payload.get("car")
    payload["car"] = (
        CarRecordFactory(NORMALIZER).build(car)
        if isinstance(car, Mapping)
        else NORMALIZER.normalize_link(car, "car")
        if car
        else None
    )
    payload["session"] = NORMALIZER.normalize_string(payload.get("session"))
    return payload


def _legacy_engine(record: Mapping[str, Any]) -> dict[str, Any]:
    payload = dict(record)
    payload["manufacturer"] = NORMALIZER.normalize_link(
        payload.get("manufacturer"),
        "manufacturer",
    )
    payload["manufacturer_status"] = NORMALIZER.normalize_status(
        payload.get("manufacturer_status"),
        ["current", "former"],
        "manufacturer_status",
    )
    payload["engines_built_in"] = NORMALIZER.normalize_link_list(
        payload.get("engines_built_in"),
        "engines_built_in",
    )
    payload["seasons"] = NORMALIZER.normalize_seasons(payload.get("seasons"))
    for name in [
        "races_entered",
        "races_started",
        "wins",
        "poles",
        "fastest_laps",
        "podiums",
        "wcc",
        "wdc",
    ]:
        payload[name] = NORMALIZER.normalize_int(payload.get(name), name)
    payload["points"] = NORMALIZER.normalize_float(payload.get("points"), "points")
    payload.setdefault("engines_built_in", [])
    payload.setdefault("seasons", [])
    return payload


def _legacy_season_summary(record: Mapping[str, Any]) -> dict[str, Any]:
    payload = dict(record)
    for name in ["season", "first", "last"]:
        payload[name] = NORMALIZER.normalize_link(payload.get(name), name)
    for name in ["races", "countries", "winners"]:
        payload[name] = NORMALIZER.normalize_int(payload.get(name), name)
    for name in ["drivers_champion_team", "constructors_champion"]:
        payload[name] = NORMALIZER.normalize_link_list(payload.get(name), name)
    payload.setdefault("drivers_champion_team", [])
    payload.setdefault("constructors_champion", [])
    return payload


@pytest.mark.parametrize(
    ("builder", "legacy", "record"),
    [
        (
            build_driver_record,
            _legacy_driver,
            {
                "driver_name": {
                    "text": "Ayrton Senna",
                    "url": "https://en.wikipedia.org/wiki/Ayrton_Senna",
                },
                "nationality": " Brazilian ",
                "is_active": "false",
                "is_world_champion": "true",
                "seasons_competed": [{"year": "1988"}, {"year": "1990"}],
                "drivers_championships": {
                    "count": "3",
                    "seasons": [{"year": "1988"}, {"year": "1990"}, {"year": "1991"}],
                },
                "race_entries": "161",
                "race_starts": "161",
                "pole_positions": "65",
                "race_wins": "41",
                "podiums": "80",
                "fastest_laps": "19",
            },
        ),
        (
            build_constructor_record,
            _legacy_constructor,
            {
                "constructor_name": {
                    "text": "McLaren",
                    "url": "https://en.wikipedia.org/wiki/McLaren",
                },
                "engine": [
                    {
                        "text": "Mercedes",
                        "url": "https://en.wikipedia.org/wiki/Mercedes",
                    },
                ],
                "based_in": [{"text": "Woking", "url": None}],
                "seasons": [{"year": 1966}],
                "licensed_in": "United Kingdom",
                "wcc_titles": "9",
            },
        ),
        (
            build_circuit_record,
            _legacy_circuit,
            {
                "circuit": {
                    "text": "Monza",
                    "url": "https://en.wikipedia.org/wiki/Monza_Circuit",
                },
                "circuit_status": "current",
                "last_length_used_km": "5.793",
                "last_length_used_mi": "3.600",
                "turns": "11",
                "grands_prix_held": "74",
                "grands_prix": [
                    {
                        "text": "Italian Grand Prix",
                        "url": "https://en.wikipedia.org/wiki/Italian_Grand_Prix",
                    },
                ],
                "seasons": [{"year": 1950}],
                "country": {
                    "text": "Italy",
                    "url": "https://en.wikipedia.org/wiki/Italy",
                },
            },
        ),
        (
            build_special_driver_record,
            _legacy_special_driver,
            {
                "driver": {
                    "text": "Nico Hülkenberg",
                    "url": "https://en.wikipedia.org/wiki/Nico_H%C3%BClkenberg",
                },
                "seasons": [{"year": "2010"}, {"year": "2023"}],
                "teams": [
                    {
                        "text": "Williams",
                        "url": "https://en.wikipedia.org/wiki/Williams_Grand_Prix_Engineering",
                    },
                ],
                "entries": "220",
                "starts": "210",
                "points": {"championship_points": "571", "total_points": "571.0"},
            },
        ),
        (
            build_grands_prix_record,
            _legacy_grands_prix,
            {
                "race_title": {
                    "text": "Miami Grand Prix",
                    "url": "https://en.wikipedia.org/wiki/Miami_Grand_Prix",
                },
                "race_status": " current ",
                "years_held": [{"year": "2022"}, {"year": "2024"}],
                "country": [
                    {
                        "text": "United States",
                        "url": "https://en.wikipedia.org/wiki/United_States",
                    },
                ],
                "circuits": "1",
                "total": "3",
            },
        ),
        (
            build_fatality_record,
            _legacy_fatality,
            {
                "driver": {
                    "text": "Sample Driver",
                    "url": "https://en.wikipedia.org/wiki/Sample",
                },
                "date": "1960-01-01",
                "age": "29",
                "event": {
                    "event": {
                        "text": "1960 Belgian GP",
                        "url": "https://en.wikipedia.org/wiki/1960_Belgian_Grand_Prix",
                    },
                    "championship": "yes",
                },
                "circuit": {
                    "text": "Spa",
                    "url": "https://en.wikipedia.org/wiki/Circuit_de_Spa-Francorchamps",
                },
                "car": {
                    "car": {
                        "text": "Lotus",
                        "url": "https://en.wikipedia.org/wiki/Lotus",
                    },
                    "formula_category": " F1 ",
                },
                "session": " Race ",
            },
        ),
        (
            build_engine_manufacturer_record,
            _legacy_engine,
            {
                "manufacturer": {
                    "text": "Honda",
                    "url": "https://en.wikipedia.org/wiki/Honda",
                },
                "manufacturer_status": "current",
                "engines_built_in": [
                    {"text": "Japan", "url": "https://en.wikipedia.org/wiki/Japan"},
                ],
                "seasons": [{"year": 1964}, {"year": 2026}],
                "races_entered": "500",
                "races_started": "498",
                "wins": "90",
                "poles": "80",
                "fastest_laps": "95",
                "podiums": "250",
                "wcc": "6",
                "wdc": "7",
                "points": "3000.5",
            },
        ),
        (
            build_season_summary_record,
            _legacy_season_summary,
            {
                "season": {
                    "text": "2023",
                    "url": "https://en.wikipedia.org/wiki/2023_Formula_One_World_Championship",
                },
                "first": {
                    "text": "Bahrain GP",
                    "url": "https://en.wikipedia.org/wiki/2023_Bahrain_Grand_Prix",
                },
                "last": {
                    "text": "Abu Dhabi GP",
                    "url": "https://en.wikipedia.org/wiki/2023_Abu_Dhabi_Grand_Prix",
                },
                "races": "22",
                "countries": "20",
                "drivers_champion_team": [
                    {
                        "text": "Red Bull Racing",
                        "url": "https://en.wikipedia.org/wiki/Red_Bull_Racing",
                    },
                ],
                "constructors_champion": [
                    {
                        "text": "Red Bull Racing",
                        "url": "https://en.wikipedia.org/wiki/Red_Bull_Racing",
                    },
                ],
                "winners": "4",
            },
        ),
    ],
)
def test_factories_snapshot_compatibility(
    builder,
    legacy,
    record: Mapping[str, Any],
) -> None:
    before_snapshot = legacy(deepcopy(record))
    after_snapshot = builder(deepcopy(record))

    assert after_snapshot == before_snapshot
