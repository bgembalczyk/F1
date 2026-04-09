from dataclasses import dataclass
from typing import Any
from typing import Callable

from models.records.builders import RECORD_BUILDERS
from models.records.type import RecordType
from scrapers.base.factory.record.adapters.callable import CallableRecordFactoryAdapter
from scrapers.base.factory.record.protocol2 import RecordFactory


@dataclass(frozen=True, slots=True)
class RecordFactoryAdapters:
    """Factory helpers for the unified RecordFactory contract."""

    adapter_builder: Callable[
        [Callable[[dict[str, Any]], Any] | type],
        RecordFactory,
    ] = CallableRecordFactoryAdapter

    def callable(
        self,
        factory: Callable[[dict[str, Any]], Any] | type,
    ) -> RecordFactory:
        if not callable(factory):
            msg = "Record factory must be callable or a record type."
            raise TypeError(msg)
        return self.adapter_builder(factory)

    def builders(self, record_type: RecordType | str) -> RecordFactory:
        if isinstance(record_type, str) and not record_type.strip():
            msg = "record_type cannot be empty."
            raise ValueError(msg)
        return self.adapter_builder(
            factory=lambda payload: RECORD_BUILDERS.build(record_type, payload),
        )


RECORD_FACTORIES = RecordFactoryAdapters()
