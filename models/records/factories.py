from collections.abc import Mapping
from typing import Any
from typing import cast

from models.mappers.field_aliases import FIELD_ALIASES
from models.mappers.field_aliases import apply_field_aliases
from models.records.base_factory import FieldNormalizer
from models.records.car import CarRecord
from models.records.circuit import CircuitRecord
from models.records.circuit_complete import CircuitCompleteRecord
from models.records.circuit_details import CircuitDetailsRecord
from models.records.constructor import ConstructorRecord
from models.records.driver import DriverRecord
from models.records.driver_championships import DriversChampionshipsRecord
from models.records.event import EventRecord
from models.records.fatality import FatalityRecord
from models.records.grand_prix import GrandsPrixRecord
from models.records.link import LinkRecord
from models.records.season import SeasonRecord
from models.records.season_summary import SeasonSummaryRecord
from models.records.special_driver import SpecialDriverRecord
from models.records.constants import WIKI_SEASON_URL

# Use the refactored normalizer from base_factory
_normalizer = FieldNormalizer()
normalize_int = _normalizer.normalize_int
normalize_float = _normalizer.normalize_float
normalize_link_value = _normalizer.normalize_link
normalize_link_list = _normalizer.normalize_link_list
normalize_seasons = _normalizer.normalize_seasons
normalize_status = _normalizer.normalize_status


def _normalize_points(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, dict):
        normalized = dict(value)
        for key in ("championship_points", "total_points"):
            if key in normalized:
                normalized[key] = normalize_float(normalized.get(key), f"points.{key}")
        return normalized
    if isinstance(value, (int, float, str)):
        return normalize_float(value, "points")
    return value


def build_link_record(record: Mapping[str, Any]) -> LinkRecord:
    normalized = normalize_link_value(record, "link") or {"text": "", "url": None}
    return cast("LinkRecord", normalized)


def build_season_record(record: Mapping[str, Any]) -> SeasonRecord:
    payload = dict(record)
    payload["year"] = normalize_int(payload.get("year"), "year")
    url = payload.get("url")
    if isinstance(url, str):
        url = url.strip() or None
    payload["url"] = url
    if payload.get("year") is not None and not payload.get("url"):
        payload["url"] = WIKI_SEASON_URL.format(year=payload["year"])
    return cast("SeasonRecord", payload)


def build_drivers_championships_record(
    record: Mapping[str, Any],
) -> DriversChampionshipsRecord:
    payload = dict(record)
    payload["count"] = normalize_int(
        payload.get("count"),
        "drivers_championships.count",
    )
    payload["count"] = payload["count"] or 0
    payload["seasons"] = normalize_seasons(payload.get("seasons"))
    return cast("DriversChampionshipsRecord", payload)


def build_driver_record(record: Mapping[str, Any]) -> DriverRecord:
    payload = apply_field_aliases(record, FIELD_ALIASES["driver"], record_name="driver")
    payload["driver"] = normalize_link_value(payload.get("driver"), "driver")
    nationality = payload.get("nationality")
    payload["nationality"] = (
        nationality.strip() if isinstance(nationality, str) else None
    )
    payload["seasons_competed"] = normalize_seasons(payload.get("seasons_competed"))
    championships = payload.get("drivers_championships") or {}
    if isinstance(championships, Mapping):
        payload["drivers_championships"] = build_drivers_championships_record(
            championships,
        )
    payload["is_active"] = bool(payload.get("is_active"))
    payload["is_world_champion"] = bool(payload.get("is_world_champion"))
    payload["race_entries"] = normalize_int(payload.get("race_entries"), "race_entries")
    payload["race_starts"] = normalize_int(payload.get("race_starts"), "race_starts")
    payload["pole_positions"] = normalize_int(
        payload.get("pole_positions"),
        "pole_positions",
    )
    payload["race_wins"] = normalize_int(payload.get("race_wins"), "race_wins")
    payload["podiums"] = normalize_int(payload.get("podiums"), "podiums")
    payload["fastest_laps"] = normalize_int(payload.get("fastest_laps"), "fastest_laps")
    payload.setdefault("drivers_championships", {"count": 0, "seasons": []})
    payload.setdefault("seasons_competed", [])
    return cast("DriverRecord", payload)


def build_special_driver_record(record: Mapping[str, Any]) -> SpecialDriverRecord:
    payload = dict(record)
    payload["driver"] = normalize_link_value(payload.get("driver"), "driver")
    payload["seasons"] = normalize_seasons(payload.get("seasons"))
    payload["teams"] = normalize_link_list(payload.get("teams"), "teams")
    payload["entries"] = normalize_int(payload.get("entries"), "entries")
    payload["starts"] = normalize_int(payload.get("starts"), "starts")
    payload["points"] = _normalize_points(payload.get("points"))
    payload.setdefault("seasons", [])
    payload.setdefault("teams", [])
    return cast("SpecialDriverRecord", payload)


def build_constructor_record(record: Mapping[str, Any]) -> ConstructorRecord:
    payload = apply_field_aliases(
        record,
        FIELD_ALIASES["constructor"],
        record_name="constructor",
    )
    payload["constructor"] = normalize_link_value(
        payload.get("constructor"),
        "constructor",
    )
    payload["engine"] = normalize_link_list(payload.get("engine"), "engine")
    payload["based_in"] = normalize_link_list(payload.get("based_in"), "based_in")
    payload["seasons"] = normalize_seasons(payload.get("seasons"))
    payload["antecedent_teams"] = normalize_link_list(
        payload.get("antecedent_teams"),
        "antecedent_teams",
    )
    licensed_in = payload.get("licensed_in")
    if isinstance(licensed_in, list):
        payload["licensed_in"] = normalize_link_list(licensed_in, "licensed_in")
    elif isinstance(licensed_in, Mapping):
        payload["licensed_in"] = normalize_link_value(licensed_in, "licensed_in")
    elif isinstance(licensed_in, str):
        payload["licensed_in"] = licensed_in.strip() or None
    payload["races_entered"] = normalize_int(
        payload.get("races_entered"),
        "races_entered",
    )
    payload["races_started"] = normalize_int(
        payload.get("races_started"),
        "races_started",
    )
    payload["drivers"] = normalize_int(payload.get("drivers"), "drivers")
    payload["total_entries"] = normalize_int(
        payload.get("total_entries"),
        "total_entries",
    )
    payload["wins"] = normalize_int(payload.get("wins"), "wins")
    payload["points"] = normalize_int(payload.get("points"), "points")
    payload["poles"] = normalize_int(payload.get("poles"), "poles")
    payload["fastest_laps"] = normalize_int(payload.get("fastest_laps"), "fastest_laps")
    payload["podiums"] = normalize_int(payload.get("podiums"), "podiums")
    payload["wcc_titles"] = normalize_int(payload.get("wcc_titles"), "wcc_titles")
    payload["wdc_titles"] = normalize_int(payload.get("wdc_titles"), "wdc_titles")
    payload.setdefault("engine", [])
    payload.setdefault("based_in", [])
    payload.setdefault("seasons", [])
    payload.setdefault("antecedent_teams", [])
    return cast("ConstructorRecord", payload)


def build_circuit_record(record: Mapping[str, Any]) -> CircuitRecord:
    payload = dict(record)
    payload["circuit"] = normalize_link_value(payload.get("circuit"), "circuit")
    payload["circuit_status"] = normalize_status(
        payload.get("circuit_status"),
        ["current", "future", "former"],
        "circuit_status",
    )
    payload["last_length_used_km"] = normalize_float(
        payload.get("last_length_used_km"),
        "last_length_used_km",
    )
    payload["last_length_used_mi"] = normalize_float(
        payload.get("last_length_used_mi"),
        "last_length_used_mi",
    )
    payload["turns"] = normalize_int(payload.get("turns"), "turns")
    payload["grands_prix"] = normalize_link_list(
        payload.get("grands_prix"),
        "grands_prix",
    )
    payload["seasons"] = normalize_seasons(payload.get("seasons"))
    payload["grands_prix_held"] = normalize_int(
        payload.get("grands_prix_held"),
        "grands_prix_held",
    )
    country = payload.get("country")
    if isinstance(country, Mapping):
        payload["country"] = normalize_link_value(country, "country")
    elif isinstance(country, str):
        payload["country"] = country.strip() or None
    payload.setdefault("grands_prix", [])
    payload.setdefault("seasons", [])
    return cast("CircuitRecord", payload)


def build_event_record(record: Mapping[str, Any]) -> EventRecord:
    payload = dict(record)
    event = payload.get("event")
    if isinstance(event, list):
        payload["event"] = normalize_link_list(event, "event")
    elif isinstance(event, (Mapping, str)):
        payload["event"] = normalize_link_value(event, "event") or (
            event.strip() if isinstance(event, str) else None
        )
    else:
        payload["event"] = None
    payload["championship"] = bool(payload.get("championship"))
    return cast("EventRecord", payload)


def build_car_record(record: Mapping[str, Any]) -> CarRecord:
    payload = dict(record)
    link = normalize_link_value(payload, "car")
    if link is None:
        link = {"text": "", "url": None}
    payload["text"] = link["text"]
    payload["url"] = link["url"]
    formula_category = payload.get("formula_category")
    if isinstance(formula_category, str):
        formula_category = formula_category.strip() or None
    if formula_category:
        payload["formula_category"] = formula_category
    else:
        payload.pop("formula_category", None)
    return cast("CarRecord", payload)


def build_fatality_record(record: Mapping[str, Any]) -> FatalityRecord:
    payload = dict(record)
    payload["driver"] = normalize_link_value(payload.get("driver"), "driver")
    payload["date"] = payload.get("date")
    payload["age"] = normalize_int(payload.get("age"), "age")
    event = payload.get("event")
    if isinstance(event, Mapping):
        payload["event"] = build_event_record(event)
    else:
        payload["event"] = None
    payload["circuit"] = normalize_link_value(payload.get("circuit"), "circuit")
    car = payload.get("car")
    if isinstance(car, Mapping):
        payload["car"] = build_car_record(car)
    else:
        payload["car"] = normalize_link_value(car, "car") if car else None
    session = payload.get("session")
    payload["session"] = session.strip() if isinstance(session, str) else None
    return cast("FatalityRecord", payload)


def build_season_summary_record(record: Mapping[str, Any]) -> SeasonSummaryRecord:
    payload = dict(record)
    payload["season"] = normalize_link_value(payload.get("season"), "season")
    payload["races"] = normalize_int(payload.get("races"), "races")
    payload["countries"] = normalize_int(payload.get("countries"), "countries")
    payload["first"] = normalize_link_value(payload.get("first"), "first")
    payload["last"] = normalize_link_value(payload.get("last"), "last")
    payload["drivers_champion_team"] = normalize_link_list(
        payload.get("drivers_champion_team"),
        "drivers_champion_team",
    )
    payload["constructors_champion"] = normalize_link_list(
        payload.get("constructors_champion"),
        "constructors_champion",
    )
    payload["winners"] = normalize_int(payload.get("winners"), "winners")
    payload.setdefault("drivers_champion_team", [])
    payload.setdefault("constructors_champion", [])
    return cast("SeasonSummaryRecord", payload)


def build_grands_prix_record(record: Mapping[str, Any]) -> GrandsPrixRecord:
    payload = dict(record)
    payload["race_title"] = normalize_link_value(
        payload.get("race_title"),
        "race_title",
    )
    race_status = payload.get("race_status")
    payload["race_status"] = (
        race_status.strip() if isinstance(race_status, str) else None
    )
    payload["years_held"] = normalize_seasons(payload.get("years_held"))
    payload["country"] = normalize_link_list(payload.get("country"), "country")
    payload["circuits"] = normalize_int(payload.get("circuits"), "circuits")
    payload["total"] = normalize_int(payload.get("total"), "total")
    payload.setdefault("years_held", [])
    payload.setdefault("country", [])
    return cast("GrandsPrixRecord", payload)


def build_circuit_details_record(record: Mapping[str, Any]) -> CircuitDetailsRecord:
    payload = dict(record)
    payload.setdefault("infobox", {})
    payload.setdefault("tables", [])
    return cast("CircuitDetailsRecord", payload)


def build_circuit_complete_record(record: Mapping[str, Any]) -> CircuitCompleteRecord:
    payload = dict(record)
    payload["grands_prix"] = normalize_link_list(
        payload.get("grands_prix"),
        "grands_prix",
    )
    payload["seasons"] = normalize_seasons(payload.get("seasons"))
    payload["grands_prix_held"] = normalize_int(
        payload.get("grands_prix_held"),
        "grands_prix_held",
    )
    payload.setdefault("history", [])
    payload.setdefault("layouts", [])
    payload.setdefault("grands_prix", [])
    payload.setdefault("seasons", [])
    return cast("CircuitCompleteRecord", payload)
