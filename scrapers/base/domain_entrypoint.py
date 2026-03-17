"""Shared abstractions for domain list-scraper entrypoints."""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.base.helpers.runner import run_and_export
from scrapers.base.run_profiles import RunProfileName
from scrapers.base.run_profiles import build_run_profile

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from scrapers.base.abc import ABCScraper
    from scrapers.base.run_config import RunConfig


def strict_quality_profile() -> RunConfig:
    """Profile with stricter diagnostics enabled."""
    return build_run_profile(RunProfileName.STRICT)


def minimal_profile() -> RunConfig:
    """Profile with a minimal production-oriented configuration."""
    return build_run_profile(RunProfileName.MINIMAL)


def minimal_debug_profile() -> RunConfig:
    """Profile with minimal checks and debug dumps enabled."""
    return build_run_profile(RunProfileName.DEBUG)


def build_run_list_scraper(
    *,
    list_scraper_cls: type[ABCScraper],
    default_output_json: str | Path,
    default_profile: Callable[[], RunConfig],
    default_output_csv: str | Path | None = None,
) -> Callable[..., None]:
    """Build a standardized `run_list_scraper` facade for domain entrypoints."""

    def run_list_scraper(*, run_config: RunConfig | None = None) -> None:
        resolved_config = run_config or default_profile()
        run_and_export(
            list_scraper_cls,
            default_output_json,
            default_output_csv,
            run_config=resolved_config,
        )

    return run_list_scraper


__all__ = [
    "build_run_list_scraper",
    "minimal_debug_profile",
    "minimal_profile",
    "strict_quality_profile",
]
