"""Backward-compatible import surface for record factory base/contracts."""

from models.records.factories.base import BaseRecordFactory
from models.records.factories.protocol import RecordBuilderProtocol

__all__ = ["BaseRecordFactory", "RecordBuilderProtocol"]
