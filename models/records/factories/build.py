from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import Literal
from typing import overload

from models.records.factories.registry import FACTORY_REGISTRY
from models.records.factories.registry import get_factory

if TYPE_CHECKING:
    from collections.abc import Mapping

    from models.records.base_factory import BaseRecordFactory
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


class RecordBuilders:
    """Object facade for building normalized record models."""

    def __init__(self, factory_registry: Mapping[str, BaseRecordFactory] | None = None):
        self._factory_registry = factory_registry or FACTORY_REGISTRY

    def _factory_for(self, record_type: str) -> BaseRecordFactory:
        return get_factory(record_type, self._factory_registry)

    @overload
    def build(
        self,
        record_type: Literal["link"],
        record: Mapping[str, Any],
    ) -> LinkRecord: ...

    @overload
    def build(
        self,
        record_type: Literal["season"],
        record: Mapping[str, Any],
    ) -> SeasonRecord: ...

    @overload
    def build(
        self,
        record_type: Literal["drivers_championships"],
        record: Mapping[str, Any],
    ) -> DriversChampionshipsRecord: ...

    @overload
    def build(
        self,
        record_type: Literal["driver"],
        record: Mapping[str, Any],
    ) -> DriverRecord: ...

    @overload
    def build(
        self,
        record_type: Literal["special_driver"],
        record: Mapping[str, Any],
    ) -> SpecialDriverRecord: ...

    @overload
    def build(
        self,
        record_type: Literal["constructor"],
        record: Mapping[str, Any],
    ) -> ConstructorRecord: ...

    @overload
    def build(
        self,
        record_type: Literal["circuit"],
        record: Mapping[str, Any],
    ) -> CircuitRecord: ...

    @overload
    def build(
        self,
        record_type: Literal["event"],
        record: Mapping[str, Any],
    ) -> EventRecord: ...

    @overload
    def build(
        self,
        record_type: Literal["car"],
        record: Mapping[str, Any],
    ) -> CarRecord: ...

    @overload
    def build(
        self,
        record_type: Literal["fatality"],
        record: Mapping[str, Any],
    ) -> FatalityRecord: ...

    @overload
    def build(
        self,
        record_type: Literal["season_summary"],
        record: Mapping[str, Any],
    ) -> SeasonSummaryRecord: ...

    @overload
    def build(
        self,
        record_type: Literal["grands_prix"],
        record: Mapping[str, Any],
    ) -> GrandsPrixRecord: ...

    @overload
    def build(
        self,
        record_type: Literal["circuit_details"],
        record: Mapping[str, Any],
    ) -> CircuitDetailsRecord: ...

    @overload
    def build(
        self,
        record_type: Literal["circuit_complete"],
        record: Mapping[str, Any],
    ) -> CircuitCompleteRecord: ...

    @overload
    def build(
        self,
        record_type: Literal["engine_manufacturer"],
        record: Mapping[str, Any],
    ) -> EngineManufacturerRecord: ...

    @overload
    def build(self, record_type: str, record: Mapping[str, Any]) -> Any: ...

    def build(self, record_type: str, record: Mapping[str, Any]) -> Any:
        return self._factory_for(record_type).build(record)

    def season(self, record: Mapping[str, Any]) -> SeasonRecord:
        return self.build("season", record)

    def driver(self, record: Mapping[str, Any]) -> DriverRecord:
        return self.build("driver", record)

    def constructor(self, record: Mapping[str, Any]) -> ConstructorRecord:
        return self.build("constructor", record)

    def circuit(self, record: Mapping[str, Any]) -> CircuitRecord:
        return self.build("circuit", record)

    def special_driver(self, record: Mapping[str, Any]) -> SpecialDriverRecord:
        return self.build("special_driver", record)

    def fatality(self, record: Mapping[str, Any]) -> FatalityRecord:
        return self.build("fatality", record)

    def season_summary(self, record: Mapping[str, Any]) -> SeasonSummaryRecord:
        return self.build("season_summary", record)

    def grands_prix(self, record: Mapping[str, Any]) -> GrandsPrixRecord:
        return self.build("grands_prix", record)

    def engine_manufacturer(
        self,
        record: Mapping[str, Any],
    ) -> EngineManufacturerRecord:
        return self.build("engine_manufacturer", record)


RECORD_BUILDERS = RecordBuilders()
