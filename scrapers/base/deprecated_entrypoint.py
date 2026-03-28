"""Shared launcher for legacy module entrypoints routed via CLI registry."""

from __future__ import annotations

from scrapers.cli import run_registered_module_for_caller


def run_deprecated_entrypoint(argv: list[str] | None = None) -> None:
    """Emit deprecation warning (if configured) and run via command registry."""
    run_registered_module_for_caller(argv)
