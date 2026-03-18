from collections.abc import Mapping
from typing import Any
from typing import cast

from models.records.car import CarRecord
from models.records.circuit import CircuitRecord
from models.records.circuit_complete import CircuitCompleteRecord
from models.records.circuit_details import CircuitDetailsRecord
from models.records.constructor import ConstructorRecord
from models.records.driver import DriverRecord
from models.records.driver_championships import DriversChampionshipsRecord
from models.records.engine_manufacturer import EngineManufacturerRecord
from models.records.event import EventRecord
from models.records.factories.registry import FactoryRegistry
from models.records.factories.registry import get_default_factory_registry
from models.records.fatality import FatalityRecord
from models.records.grand_prix import GrandsPrixRecord
from models.records.link import LinkRecord
from models.records.season import SeasonRecord
from models.records.season_summary import SeasonSummaryRecord
from models.records.special_driver import SpecialDriverRecord


class RecordBuilder:
    """Thin facade for building records from an explicit factory registry."""

    def __init__(self, registry: FactoryRegistry):
        self.registry = registry

    def build_record(self, record_type: str, record: Mapping[str, Any]) -> Any:
        factory = self.registry.get(record_type)
        if factory is None:
            msg = f"Unsupported record type: {record_type}"
            raise ValueError(msg)
        return factory.build(record)


def _get_record_builder(registry: FactoryRegistry | None = None) -> RecordBuilder:
    return RecordBuilder(registry or get_default_factory_registry())


def build_record(
    record_type: str,
    record: Mapping[str, Any],
    *,
    registry: FactoryRegistry | None = None,
) -> Any:
    return _get_record_builder(registry).build_record(record_type, record)


def build_link_record(
    record: Mapping[str, Any],
    *,
    registry: FactoryRegistry | None = None,
) -> LinkRecord:
    return cast("LinkRecord", build_record("link", record, registry=registry))


def build_season_record(
    record: Mapping[str, Any],
    *,
    registry: FactoryRegistry | None = None,
) -> SeasonRecord:
    return cast("SeasonRecord", build_record("season", record, registry=registry))


def build_drivers_championships_record(
    record: Mapping[str, Any],
    *,
    registry: FactoryRegistry | None = None,
) -> DriversChampionshipsRecord:
    return cast(
        "DriversChampionshipsRecord",
        build_record("drivers_championships", record, registry=registry),
    )


def build_driver_record(
    record: Mapping[str, Any],
    *,
    registry: FactoryRegistry | None = None,
) -> DriverRecord:
    return cast("DriverRecord", build_record("driver", record, registry=registry))


def build_special_driver_record(
    record: Mapping[str, Any],
    *,
    registry: FactoryRegistry | None = None,
) -> SpecialDriverRecord:
    return cast(
        "SpecialDriverRecord",
        build_record("special_driver", record, registry=registry),
    )


def build_constructor_record(
    record: Mapping[str, Any],
    *,
    registry: FactoryRegistry | None = None,
) -> ConstructorRecord:
    return cast(
        "ConstructorRecord",
        build_record("constructor", record, registry=registry),
    )


def build_circuit_record(
    record: Mapping[str, Any],
    *,
    registry: FactoryRegistry | None = None,
) -> CircuitRecord:
    return cast("CircuitRecord", build_record("circuit", record, registry=registry))


def build_event_record(
    record: Mapping[str, Any],
    *,
    registry: FactoryRegistry | None = None,
) -> EventRecord:
    return cast("EventRecord", build_record("event", record, registry=registry))


def build_car_record(
    record: Mapping[str, Any],
    *,
    registry: FactoryRegistry | None = None,
) -> CarRecord:
    return cast("CarRecord", build_record("car", record, registry=registry))


def build_fatality_record(
    record: Mapping[str, Any],
    *,
    registry: FactoryRegistry | None = None,
) -> FatalityRecord:
    return cast("FatalityRecord", build_record("fatality", record, registry=registry))


def build_season_summary_record(
    record: Mapping[str, Any],
    *,
    registry: FactoryRegistry | None = None,
) -> SeasonSummaryRecord:
    return cast(
        "SeasonSummaryRecord",
        build_record("season_summary", record, registry=registry),
    )


def build_grands_prix_record(
    record: Mapping[str, Any],
    *,
    registry: FactoryRegistry | None = None,
) -> GrandsPrixRecord:
    return cast(
        "GrandsPrixRecord",
        build_record("grands_prix", record, registry=registry),
    )


def build_circuit_details_record(
    record: Mapping[str, Any],
    *,
    registry: FactoryRegistry | None = None,
) -> CircuitDetailsRecord:
    return cast(
        "CircuitDetailsRecord",
        build_record("circuit_details", record, registry=registry),
    )


def build_circuit_complete_record(
    record: Mapping[str, Any],
    *,
    registry: FactoryRegistry | None = None,
) -> CircuitCompleteRecord:
    return cast(
        "CircuitCompleteRecord",
        build_record("circuit_complete", record, registry=registry),
    )


def build_engine_manufacturer_record(
    record: Mapping[str, Any],
    *,
    registry: FactoryRegistry | None = None,
) -> EngineManufacturerRecord:
    return cast(
        "EngineManufacturerRecord",
        build_record("engine_manufacturer", record, registry=registry),
    )
