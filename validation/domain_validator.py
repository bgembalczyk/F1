"""Compatibility wrapper for the shared record validator contract."""

from validation.validator_base import RecordValidator


class BaseDomainRecordValidator(RecordValidator):
    """Backward-compatible alias for the shared validator base class."""
