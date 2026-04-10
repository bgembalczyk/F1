"""Backward-compatible aliases for deprecated protocol module path."""

from models.records.factories.protocol import RecordBuilder
from models.records.factories.protocol import RecordBuilderProtocol

# Deprecated compatibility aliases.
RecordFactory = RecordBuilder
RecordFactoryProtocol = RecordBuilderProtocol

__all__ = [
    "RecordBuilder",
    "RecordBuilderProtocol",
    "RecordFactory",
    "RecordFactoryProtocol",
]
