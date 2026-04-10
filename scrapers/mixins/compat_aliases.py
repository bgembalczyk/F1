"""Compatibility aliases kept as thin transition layer."""

from scrapers.mixins.behavior_mixins import RunDiagnosticsMixin


class RetryMixin(RunDiagnosticsMixin):
    """Compatibility alias for retry behavior."""


class DebugDumpMixin(RunDiagnosticsMixin):
    """Compatibility alias for debug payload dump behavior."""


class ValidationMixin(RunDiagnosticsMixin):
    """Compatibility alias for required-field validation behavior."""


__all__ = ["RetryMixin", "DebugDumpMixin", "ValidationMixin"]
