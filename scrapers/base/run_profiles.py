"""Central run-profile definitions used by scraper entrypoints."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Literal

from scrapers.base.run_config import RunConfig


@dataclass(frozen=True)
class RunPathConfig:
    """Canonical default locations for wiki outputs and debug artifacts."""

    wiki_output_dir: Path = Path("../../data/wiki")
    debug_dir: Path = Path("../../data/debug")


DEFAULT_RUN_PATHS = RunPathConfig()


class RunProfileName(str, Enum):
    STRICT = "strict"
    MINIMAL = "minimal"
    DEBUG = "debug"
    DEPRECATED = "deprecated"


RunProfileSelector = (
    RunProfileName
    | Literal[
        "strict",
        "minimal",
        "debug",
        "deprecated",
    ]
)


def _coerce_profile(profile: RunProfileSelector) -> RunProfileName:
    if isinstance(profile, RunProfileName):
        return profile
    return RunProfileName(profile)


def build_run_profile(
    profile: RunProfileSelector,
    *,
    paths: RunPathConfig = DEFAULT_RUN_PATHS,
) -> RunConfig:
    """Build ``RunConfig`` for a named profile."""
    normalized_profile = _coerce_profile(profile)

    if normalized_profile is RunProfileName.STRICT:
        return RunConfig(
            output_dir=paths.wiki_output_dir,
            include_urls=True,
            debug_dir=paths.debug_dir,
            quality_report=True,
            error_report=False,
        )

    if normalized_profile is RunProfileName.MINIMAL:
        return RunConfig(
            output_dir=paths.wiki_output_dir,
            include_urls=True,
        )

    if normalized_profile in {RunProfileName.DEBUG, RunProfileName.DEPRECATED}:
        return RunConfig(
            output_dir=paths.wiki_output_dir,
            include_urls=True,
            debug_dir=paths.debug_dir,
        )

    raise ValueError(f"Unsupported run profile: {normalized_profile!r}")


__all__ = [
    "DEFAULT_RUN_PATHS",
    "RunPathConfig",
    "RunProfileName",
    "RunProfileSelector",
    "build_run_profile",
]
