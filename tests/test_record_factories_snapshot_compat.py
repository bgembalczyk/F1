from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from models.mappers.field_aliases import FIELD_ALIASES
from models.mappers.field_aliases import apply_field_aliases
from models.records.factories.drivers_championships_factory import (
    DriversChampionshipsRecordFactory,
)
from models.records.factories.helpers import (
    normalize_optional_link_list_or_link_or_string,
)
from models.records.factories.helpers import normalize_optional_link_or_string
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
