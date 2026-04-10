"""Backward-compatible aliases for diagnostics-related mixins."""

from scrapers.mixins.run_diagnostics import RunDiagnosticsMixin


class RetryMixin(RunDiagnosticsMixin):
    """Compatibility alias for retry behavior."""


class DebugDumpMixin(RunDiagnosticsMixin):
    """Compatibility alias for debug payload dump behavior."""


class ValidationMixin(RunDiagnosticsMixin):
    """Compatibility alias for required-field validation behavior."""
