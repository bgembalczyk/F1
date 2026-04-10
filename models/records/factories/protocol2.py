"""Backward-compatible aliases for deprecated protocol module path."""

from models.records.factories.protocol import RecordBuilder
from models.records.factories.protocol import RecordBuilderProtocol
from models.records.factories.protocol import RecordFactory
from models.records.factories.protocol import RecordFactoryProtocol

__all__ = [
    "RecordBuilder",
    "RecordFactory",
    "RecordFactoryProtocol",
    "RecordBuilderProtocol",
]
