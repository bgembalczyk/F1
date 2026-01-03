from typing import Any, Mapping, cast

from models.scrape_types.circuit_row import CircuitRow
from models.scrape_types.constructor_row import ConstructorRow
from models.scrape_types.driver_championships_payload import DriverChampionshipsPayload
from models.scrape_types.driver_row import DriverRow
from models.scrape_types.fatality_row import FatalityRow
from models.scrape_types.season_ref_payload import SeasonRefPayload


def _from_mapping(record: Mapping[str, Any]) -> dict[str, Any]:
    return dict(record)


def build_season_ref_payload(record: Mapping[str, Any]) -> SeasonRefPayload:
    return cast(SeasonRefPayload, _from_mapping(record))


def build_driver_championships_payload(
    record: Mapping[str, Any],
) -> DriverChampionshipsPayload:
    payload = _from_mapping(record)
    payload.setdefault("count", 0)
    payload.setdefault("seasons", [])
    return cast(DriverChampionshipsPayload, payload)


def build_driver_row(record: Mapping[str, Any]) -> DriverRow:
    payload = _from_mapping(record)
    payload.setdefault("seasons_competed", [])
    payload.setdefault("drivers_championships", {"count": 0, "seasons": []})
    return cast(DriverRow, payload)


def build_circuit_row(record: Mapping[str, Any]) -> CircuitRow:
    payload = _from_mapping(record)
    payload.setdefault("grands_prix", [])
    payload.setdefault("seasons", [])
    return cast(CircuitRow, payload)


def build_constructor_row(record: Mapping[str, Any]) -> ConstructorRow:
    payload = _from_mapping(record)
    payload.setdefault("engine", [])
    payload.setdefault("based_in", [])
    payload.setdefault("seasons", [])
    payload.setdefault("antecedent_teams", [])
    return cast(ConstructorRow, payload)


def build_fatality_row(record: Mapping[str, Any]) -> FatalityRow:
    return cast(FatalityRow, _from_mapping(record))
