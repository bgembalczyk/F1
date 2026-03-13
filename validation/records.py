"""Backward-compatible re-exports for validation record types and validators.

The implementation has been split into focused modules:
- ``validation.validator_base`` – ``RecordValidator`` abstract base class
- ``validation.domain_validator`` – ``BaseDomainRecordValidator``

All public names are re-exported from here so that existing imports continue
to work without modification.
"""
# Re-export everything so existing ``from validation.records import X`` calls
# keep working unchanged.
from validation.issue import ValidationIssue as ValidationIssue
from validation.schemas import RecordSchema as RecordSchema
from validation.schemas import NestedSchema as NestedSchema
from validation.validator_base import ExportRecord as ExportRecord
from validation.validator_base import RecordValidator as RecordValidator
from validation.domain_validator import BaseDomainRecordValidator as BaseDomainRecordValidator

__all__ = [
    "ExportRecord",
    "RecordValidator",
    "BaseDomainRecordValidator",
    "ValidationIssue",
    "RecordSchema",
    "NestedSchema",
]
