from collections.abc import Mapping
from typing import Any, cast

from models.records.car import CarRecord
from models.records.circuit import CircuitRecord
from models.records.circuit_complete import CircuitCompleteRecord
from models.records.circuit_details import CircuitDetailsRecord
from models.records.constructor import ConstructorRecord
from models.records.driver import DriverRecord
from models.records.driver_championships import DriversChampionshipsRecord
from models.records.engine_manufacturer import EngineManufacturerRecord
from models.records.event import EventRecord
from models.records.fatality import FatalityRecord
from models.records.grand_prix import GrandsPrixRecord
from models.records.link import LinkRecord
from models.records.season import SeasonRecord
from models.records.season_summary import SeasonSummaryRecord
from models.records.special_driver import SpecialDriverRecord
from models.records.factories.registry import FACTORY_REGISTRY


def build_record(record_type: str, record: Mapping[str, Any]) -> Any:
    factory = FACTORY_REGISTRY.get(record_type)
    if factory is None:
        raise ValueError(f"Unsupported record type: {record_type}")
    return factory.build(record)


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
