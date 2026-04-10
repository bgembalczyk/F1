"""Backward-compatible import surface for record factory base/contracts."""

from models.records.factories.base import BaseRecordFactory
from models.records.factories.protocol import RecordBuilder as RecordBuilderProtocol
from models.records.factories.protocol import RecordFactoryProtocol

__all__ = ["BaseRecordFactory", "RecordFactoryProtocol", "RecordBuilderProtocol"]
