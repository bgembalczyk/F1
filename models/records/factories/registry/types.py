from collections.abc import Mapping

from models.records.factories.protocol import RecordBuilder

FactoryRegistry = Mapping[str, RecordBuilder]
MutableFactoryRegistry = dict[str, RecordBuilder]

__all__ = ["FactoryRegistry", "MutableFactoryRegistry"]
