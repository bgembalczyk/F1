from collections.abc import Mapping
from typing import Any
from typing import cast

from models.mappers.field_aliases import FIELD_ALIASES
from models.records.base_factory import BaseRecordFactory
from models.records.car import CarRecord
from models.records.circuit import CircuitRecord
from models.records.circuit_complete import CircuitCompleteRecord
from models.records.circuit_details import CircuitDetailsRecord
from models.records.constants import WIKI_SEASON_URL
from models.records.constructor import ConstructorRecord
from models.records.driver import DriverRecord
from models.records.driver_championships import DriversChampionshipsRecord
from models.records.engine_manufacturer import EngineManufacturerRecord
from models.records.event import EventRecord
from models.records.fatality import FatalityRecord
from models.records.field_normalizer import FieldNormalizer
from models.records.grand_prix import GrandsPrixRecord
from models.records.link import LinkRecord
from models.records.season import SeasonRecord
from models.records.season_summary import SeasonSummaryRecord
from models.records.special_driver import SpecialDriverRecord


def _normalize_points(normalizer: FieldNormalizer, value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, dict):
        normalized = dict(value)
        for key in ("championship_points", "total_points"):
            if key in normalized:
                normalized[key] = normalizer.normalize_float(
                    normalized.get(key),
                    f"points.{key}",
                )
        return normalized
    if isinstance(value, int | float | str):
        return normalizer.normalize_float(value, "points")
    return value


class LinkRecordFactory(BaseRecordFactory):
    def build(self, record: Mapping[str, Any]) -> LinkRecord:
        normalized = self.normalizer.normalize_link(record, "link") or {"text": "", "url": None}
        return cast("LinkRecord", normalized)


class SeasonRecordFactory(BaseRecordFactory):
    def build(self, record: Mapping[str, Any]) -> SeasonRecord:
        payload = dict(record)
        self.normalize_int_fields(payload, ["year"])
        self.normalize_string_field(payload, "url")
        if payload.get("year") is not None and not payload.get("url"):
            payload["url"] = WIKI_SEASON_URL.format(year=payload["year"])
        return cast("SeasonRecord", payload)


class DriversChampionshipsRecordFactory(BaseRecordFactory):
    def build(self, record: Mapping[str, Any]) -> DriversChampionshipsRecord:
        payload = dict(record)
        self.normalize_int_fields(payload, ["count"])
        payload["count"] = payload["count"] or 0
        self.normalize_seasons_fields(payload, ["seasons"])
        return cast("DriversChampionshipsRecord", payload)


class DriverRecordFactory(BaseRecordFactory):
    def __init__(self, normalizer: FieldNormalizer | None = None):
        super().__init__(normalizer)
        self.championships_factory = DriversChampionshipsRecordFactory(self.normalizer)

    def build(self, record: Mapping[str, Any]) -> DriverRecord:
        payload = self.apply_aliases(record, FIELD_ALIASES["driver"], "driver")
        self.normalize_link_fields(payload, ["driver"])
        self.normalize_string_field(payload, "nationality")
        self.normalize_seasons_fields(payload, ["seasons_competed"])

        championships = payload.get("drivers_championships") or {}
        if isinstance(championships, Mapping):
            payload["drivers_championships"] = self.championships_factory.build(championships)

        payload["is_active"] = self.normalizer.normalize_bool(payload.get("is_active"))
        payload["is_world_champion"] = self.normalizer.normalize_bool(payload.get("is_world_champion"))
        self.normalize_int_fields(
            payload,
            [
                "race_entries",
                "race_starts",
                "pole_positions",
                "race_wins",
                "podiums",
                "fastest_laps",
            ],
        )
        self.set_defaults(
            payload,
            {
                "drivers_championships": {"count": 0, "seasons": []},
                "seasons_competed": [],
            },
        )
        return cast("DriverRecord", payload)


class SpecialDriverRecordFactory(BaseRecordFactory):
    def build(self, record: Mapping[str, Any]) -> SpecialDriverRecord:
        payload = dict(record)
        self.normalize_link_fields(payload, ["driver"])
        self.normalize_seasons_fields(payload, ["seasons"])
        self.normalize_link_list_fields(payload, ["teams"])
        self.normalize_int_fields(payload, ["entries", "starts"])
        payload["points"] = _normalize_points(self.normalizer, payload.get("points"))
        self.set_defaults(payload, {"seasons": [], "teams": []})
        return cast("SpecialDriverRecord", payload)


class ConstructorRecordFactory(BaseRecordFactory):
    def build(self, record: Mapping[str, Any]) -> ConstructorRecord:
        payload = self.apply_aliases(record, FIELD_ALIASES["constructor"], "constructor")
        self.normalize_link_fields(payload, ["constructor"])
        self.normalize_link_list_fields(
            payload,
            ["engine", "based_in", "antecedent_teams"],
        )
        self.normalize_seasons_fields(payload, ["seasons"])

        licensed_in = payload.get("licensed_in")
        if isinstance(licensed_in, list):
            payload["licensed_in"] = self.normalizer.normalize_link_list(licensed_in, "licensed_in")
        elif isinstance(licensed_in, Mapping):
            payload["licensed_in"] = self.normalizer.normalize_link(licensed_in, "licensed_in")
        elif isinstance(licensed_in, str):
            payload["licensed_in"] = self.normalizer.normalize_string(licensed_in)

        self.normalize_int_fields(
            payload,
            [
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
            ],
        )
        self.set_defaults(
            payload,
            {
                "engine": [],
                "based_in": [],
                "seasons": [],
                "antecedent_teams": [],
            },
        )
        return cast("ConstructorRecord", payload)


class CircuitRecordFactory(BaseRecordFactory):
    def build(self, record: Mapping[str, Any]) -> CircuitRecord:
        payload = dict(record)
        self.normalize_link_fields(payload, ["circuit"])
        payload["circuit_status"] = self.normalizer.normalize_status(
            payload.get("circuit_status"),
            ["current", "future", "former"],
            "circuit_status",
        )
        self.normalize_float_fields(payload, ["last_length_used_km", "last_length_used_mi"])
        self.normalize_int_fields(payload, ["turns", "grands_prix_held"])
        self.normalize_link_list_fields(payload, ["grands_prix"])
        self.normalize_seasons_fields(payload, ["seasons"])

        country = payload.get("country")
        if isinstance(country, Mapping):
            payload["country"] = self.normalizer.normalize_link(country, "country")
        elif isinstance(country, str):
            payload["country"] = self.normalizer.normalize_string(country)

        self.set_defaults(payload, {"grands_prix": [], "seasons": []})
        return cast("CircuitRecord", payload)


class EventRecordFactory(BaseRecordFactory):
    def build(self, record: Mapping[str, Any]) -> EventRecord:
        payload = dict(record)
        event = payload.get("event")
        if isinstance(event, list):
            payload["event"] = self.normalizer.normalize_link_list(event, "event")
        elif isinstance(event, Mapping | str):
            payload["event"] = self.normalizer.normalize_link(event, "event") or (
                self.normalizer.normalize_string(event) if isinstance(event, str) else None
            )
        else:
            payload["event"] = None
        payload["championship"] = self.normalizer.normalize_bool(payload.get("championship"))
        return cast("EventRecord", payload)


class CarRecordFactory(BaseRecordFactory):
    def build(self, record: Mapping[str, Any]) -> CarRecord:
        payload = dict(record)
        link = self.normalizer.normalize_link(payload, "car")
        if link is None:
            link = {"text": "", "url": None}
        payload["text"] = link["text"]
        payload["url"] = link["url"]
        formula_category = self.normalizer.normalize_string(payload.get("formula_category"))
        if formula_category:
            payload["formula_category"] = formula_category
        else:
            payload.pop("formula_category", None)
        return cast("CarRecord", payload)


class FatalityRecordFactory(BaseRecordFactory):
    def __init__(self, normalizer: FieldNormalizer | None = None):
        super().__init__(normalizer)
        self.event_factory = EventRecordFactory(self.normalizer)
        self.car_factory = CarRecordFactory(self.normalizer)

    def build(self, record: Mapping[str, Any]) -> FatalityRecord:
        payload = dict(record)
        self.normalize_link_fields(payload, ["driver", "circuit"])
        self.normalize_int_fields(payload, ["age"])

        event = payload.get("event")
        payload["event"] = self.event_factory.build(event) if isinstance(event, Mapping) else None

        car = payload.get("car")
        if isinstance(car, Mapping):
            payload["car"] = self.car_factory.build(car)
        else:
            payload["car"] = self.normalizer.normalize_link(car, "car") if car else None

        self.normalize_string_field(payload, "session")
        return cast("FatalityRecord", payload)


class SeasonSummaryRecordFactory(BaseRecordFactory):
    def build(self, record: Mapping[str, Any]) -> SeasonSummaryRecord:
        payload = dict(record)
        self.normalize_link_fields(payload, ["season", "first", "last"])
        self.normalize_int_fields(payload, ["races", "countries", "winners"])
        self.normalize_link_list_fields(
            payload,
            ["drivers_champion_team", "constructors_champion"],
        )
        self.set_defaults(
            payload,
            {
                "drivers_champion_team": [],
                "constructors_champion": [],
            },
        )
        return cast("SeasonSummaryRecord", payload)


class GrandsPrixRecordFactory(BaseRecordFactory):
    def build(self, record: Mapping[str, Any]) -> GrandsPrixRecord:
        payload = dict(record)
        self.normalize_link_fields(payload, ["race_title"])
        self.normalize_string_field(payload, "race_status")
        self.normalize_seasons_fields(payload, ["years_held"])
        self.normalize_link_list_fields(payload, ["country"])
        self.normalize_int_fields(payload, ["circuits", "total"])
        self.set_defaults(payload, {"years_held": [], "country": []})
        return cast("GrandsPrixRecord", payload)


class CircuitDetailsRecordFactory(BaseRecordFactory):
    def build(self, record: Mapping[str, Any]) -> CircuitDetailsRecord:
        payload = dict(record)
        self.set_defaults(payload, {"infobox": {}, "tables": []})
        return cast("CircuitDetailsRecord", payload)


class CircuitCompleteRecordFactory(BaseRecordFactory):
    def build(self, record: Mapping[str, Any]) -> CircuitCompleteRecord:
        payload = dict(record)
        self.normalize_link_list_fields(payload, ["grands_prix"])
        self.normalize_seasons_fields(payload, ["seasons"])
        self.normalize_int_fields(payload, ["grands_prix_held"])
        self.set_defaults(
            payload,
            {
                "history": [],
                "layouts": [],
                "grands_prix": [],
                "seasons": [],
            },
        )
        return cast("CircuitCompleteRecord", payload)


class EngineManufacturerRecordFactory(BaseRecordFactory):
    def build(self, record: Mapping[str, Any]) -> EngineManufacturerRecord:
        payload = dict(record)
        self.normalize_link_fields(payload, ["manufacturer"])
        payload["manufacturer_status"] = self.normalizer.normalize_status(
            payload.get("manufacturer_status"),
            ["current", "former"],
            "manufacturer_status",
        )
        self.normalize_link_list_fields(payload, ["engines_built_in"])
        self.normalize_seasons_fields(payload, ["seasons"])
        self.normalize_int_fields(
            payload,
            [
                "races_entered",
                "races_started",
                "wins",
                "poles",
                "fastest_laps",
                "podiums",
                "wcc",
                "wdc",
            ],
        )
        self.normalize_float_fields(payload, ["points"])
        self.set_defaults(payload, {"engines_built_in": [], "seasons": []})
        return cast("EngineManufacturerRecord", payload)


FACTORY_REGISTRY: dict[str, BaseRecordFactory] = {
    "link": LinkRecordFactory(),
    "season": SeasonRecordFactory(),
    "drivers_championships": DriversChampionshipsRecordFactory(),
    "driver": DriverRecordFactory(),
    "special_driver": SpecialDriverRecordFactory(),
    "constructor": ConstructorRecordFactory(),
    "circuit": CircuitRecordFactory(),
    "event": EventRecordFactory(),
    "car": CarRecordFactory(),
    "fatality": FatalityRecordFactory(),
    "season_summary": SeasonSummaryRecordFactory(),
    "grands_prix": GrandsPrixRecordFactory(),
    "circuit_details": CircuitDetailsRecordFactory(),
    "circuit_complete": CircuitCompleteRecordFactory(),
    "engine_manufacturer": EngineManufacturerRecordFactory(),
}


def build_record(record_type: str, record: Mapping[str, Any]) -> Any:
    factory = FACTORY_REGISTRY.get(record_type)
    if factory is None:
        raise ValueError(f"Unsupported record type: {record_type}")
    return factory.build(record)


# Compatibility wrappers for existing imports/usages.
def build_link_record(record: Mapping[str, Any]) -> LinkRecord:
    return cast("LinkRecord", build_record("link", record))


def build_season_record(record: Mapping[str, Any]) -> SeasonRecord:
    return cast("SeasonRecord", build_record("season", record))


def build_drivers_championships_record(record: Mapping[str, Any]) -> DriversChampionshipsRecord:
    return cast("DriversChampionshipsRecord", build_record("drivers_championships", record))


def build_driver_record(record: Mapping[str, Any]) -> DriverRecord:
    return cast("DriverRecord", build_record("driver", record))


def build_special_driver_record(record: Mapping[str, Any]) -> SpecialDriverRecord:
    return cast("SpecialDriverRecord", build_record("special_driver", record))


def build_constructor_record(record: Mapping[str, Any]) -> ConstructorRecord:
    return cast("ConstructorRecord", build_record("constructor", record))


def build_circuit_record(record: Mapping[str, Any]) -> CircuitRecord:
    return cast("CircuitRecord", build_record("circuit", record))


def build_event_record(record: Mapping[str, Any]) -> EventRecord:
    return cast("EventRecord", build_record("event", record))


def build_car_record(record: Mapping[str, Any]) -> CarRecord:
    return cast("CarRecord", build_record("car", record))


def build_fatality_record(record: Mapping[str, Any]) -> FatalityRecord:
    return cast("FatalityRecord", build_record("fatality", record))


def build_season_summary_record(record: Mapping[str, Any]) -> SeasonSummaryRecord:
    return cast("SeasonSummaryRecord", build_record("season_summary", record))


def build_grands_prix_record(record: Mapping[str, Any]) -> GrandsPrixRecord:
    return cast("GrandsPrixRecord", build_record("grands_prix", record))


def build_circuit_details_record(record: Mapping[str, Any]) -> CircuitDetailsRecord:
    return cast("CircuitDetailsRecord", build_record("circuit_details", record))


def build_circuit_complete_record(record: Mapping[str, Any]) -> CircuitCompleteRecord:
    return cast("CircuitCompleteRecord", build_record("circuit_complete", record))


def build_engine_manufacturer_record(record: Mapping[str, Any]) -> EngineManufacturerRecord:
    return cast("EngineManufacturerRecord", build_record("engine_manufacturer", record))
