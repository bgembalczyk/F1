from typing import Any, Mapping, cast

from models.records.circuit import CircuitRecord
from models.records.constructor import ConstructorRecord
from models.records.driver import DriverRecord


def build_driver_record(record: Mapping[str, Any]) -> DriverRecord:
    payload = dict(record)
    payload.setdefault("seasons_competed", [])
    payload.setdefault("drivers_championships", {"count": 0, "seasons": []})
    return cast(DriverRecord, payload)


def build_circuit_record(record: Mapping[str, Any]) -> CircuitRecord:
    payload = dict(record)
    payload.setdefault("grands_prix", [])
    payload.setdefault("seasons", [])
    return cast(CircuitRecord, payload)


def build_constructor_record(record: Mapping[str, Any]) -> ConstructorRecord:
    payload = dict(record)
    payload.setdefault("engine", [])
    payload.setdefault("based_in", [])
    payload.setdefault("seasons", [])
    payload.setdefault("antecedent_teams", [])
    return cast(ConstructorRecord, payload)
