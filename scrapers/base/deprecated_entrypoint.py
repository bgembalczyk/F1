"""Shared legacy-module launcher for deprecated module entrypoints."""

from __future__ import annotations

from scrapers.cli import run_current_legacy_wrapper


def run_deprecated_entrypoint(argv: list[str] | None = None) -> None:
    """Emit deprecation warning and delegate execution to canonical CLI wrapper."""
    run_current_legacy_wrapper(argv)
