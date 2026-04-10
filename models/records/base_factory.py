"""Backward-compatible import surface for record factory base/contracts."""

from models.records.factories.base import BaseRecordFactory
from models.records.factories.protocol import RecordBuilder as RecordBuilderProtocol

# Deprecated alias maintained for compatibility imports.
RecordFactoryProtocol = RecordBuilderProtocol

__all__ = ["BaseRecordFactory", "RecordBuilderProtocol", "RecordFactoryProtocol"]
