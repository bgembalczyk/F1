from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from models.records.factories.build import RECORD_BUILDERS
from models.records.factories.build import RecordType
from models.records.factories.protocol import RecordBuilder
from scrapers.adapters.factories.callable import CallableRecordFactoryAdapter


@dataclass(frozen=True, slots=True)
class RecordFactoryAdapters:
    """Factory helpers for the unified record builder contract."""

    adapter_builder: Callable[
        [Callable[[dict[str, Any]], Any] | type],
        RecordBuilder,
    ] = CallableRecordFactoryAdapter

    def callable(
        self,
        factory: Callable[[dict[str, Any]], Any] | type,
    ) -> RecordBuilder:
        if not callable(factory):
            msg = "Record factory must be callable or a record type."
            raise TypeError(msg)
        return self.adapter_builder(factory)

    def builders(self, record_type: RecordType | str) -> RecordBuilder:
        if isinstance(record_type, str) and not record_type.strip():
            msg = "record_type cannot be empty."
            raise ValueError(msg)
        return self.adapter_builder(
            factory=lambda payload: RECORD_BUILDERS.build(record_type, payload),
        )


RECORD_FACTORIES = RecordFactoryAdapters()
