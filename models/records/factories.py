from typing import Any, Mapping, cast

from models.records.circuit import CircuitRecord
from models.records.circuit_complete import CircuitCompleteRecord
from models.records.circuit_details import CircuitDetailsRecord
from models.records.constructor import ConstructorRecord
from models.records.driver import DriverRecord
from models.records.driver_championships import DriversChampionshipsRecord
from models.records.fatality import FatalityRecord
from models.records.link import LinkRecord
from models.records.season import SeasonRecord


def _from_mapping(record: Mapping[str, Any]) -> dict[str, Any]:
    return dict(record)


def build_link_record(record: Mapping[str, Any]) -> LinkRecord:
    return cast(LinkRecord, _from_mapping(record))


def build_season_record(record: Mapping[str, Any]) -> SeasonRecord:
    return cast(SeasonRecord, _from_mapping(record))


def build_driver_championships_record(
    record: Mapping[str, Any],
) -> DriversChampionshipsRecord:
    payload = _from_mapping(record)
    payload.setdefault("count", 0)
    payload.setdefault("seasons", [])
    return cast(DriversChampionshipsRecord, payload)


def build_driver_record(record: Mapping[str, Any]) -> DriverRecord:
    payload = _from_mapping(record)
    payload.setdefault("seasons_competed", [])
    payload.setdefault("drivers_championships", {"count": 0, "seasons": []})
    return cast(DriverRecord, payload)


def build_circuit_record(record: Mapping[str, Any]) -> CircuitRecord:
    payload = _from_mapping(record)
    payload.setdefault("grands_prix", [])
    payload.setdefault("seasons", [])
    return cast(CircuitRecord, payload)


def build_constructor_record(record: Mapping[str, Any]) -> ConstructorRecord:
    payload = _from_mapping(record)
    payload.setdefault("engine", [])
    payload.setdefault("based_in", [])
    payload.setdefault("seasons", [])
    payload.setdefault("antecedent_teams", [])
    return cast(ConstructorRecord, payload)


def build_circuit_complete_record(record: Mapping[str, Any]) -> CircuitCompleteRecord:
    return cast(CircuitCompleteRecord, _from_mapping(record))


def build_circuit_details_record(record: Mapping[str, Any]) -> CircuitDetailsRecord:
    return cast(CircuitDetailsRecord, _from_mapping(record))


def build_fatality_record(record: Mapping[str, Any]) -> FatalityRecord:
    return cast(FatalityRecord, _from_mapping(record))
