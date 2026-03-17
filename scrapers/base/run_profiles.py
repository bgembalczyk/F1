"""Central run-profile definitions used by scraper entrypoints."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Literal

if TYPE_CHECKING:
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
    from scrapers.base.run_config import RunConfig

    normalized_profile = _coerce_profile(profile)
    config_builders: dict[RunProfileName, Callable[[], RunConfig]] = {
        RunProfileName.STRICT: lambda: RunConfig(
            output_dir=paths.wiki_output_dir,
            include_urls=True,
            debug_dir=paths.debug_dir,
            quality_report=True,
            error_report=False,
        ),
        RunProfileName.MINIMAL: lambda: RunConfig(
            output_dir=paths.wiki_output_dir,
            include_urls=True,
        ),
        RunProfileName.DEBUG: lambda: RunConfig(
            output_dir=paths.wiki_output_dir,
            include_urls=True,
            debug_dir=paths.debug_dir,
        ),
        RunProfileName.DEPRECATED: lambda: RunConfig(
            output_dir=paths.wiki_output_dir,
            include_urls=True,
            debug_dir=paths.debug_dir,
        ),
    }
    builder = config_builders.get(normalized_profile)
    if builder is not None:
        return builder()

    msg = f"Unsupported run profile: {normalized_profile!r}"
    raise ValueError(msg)
