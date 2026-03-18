"""Central run-profile definitions used by scraper entrypoints."""

from __future__ import annotations

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

    def resolve(self, path_name: RunPathName) -> Path:
        return getattr(self, path_name.value)


DEFAULT_RUN_PATHS = RunPathConfig()


class RunProfileName(str, Enum):
    STRICT = "strict"
    MINIMAL = "minimal"
    DEBUG = "debug"
    DEPRECATED = "deprecated"


class RunPathName(str, Enum):
    WIKI_OUTPUT_DIR = "wiki_output_dir"
    DEBUG_DIR = "debug_dir"


@dataclass(frozen=True)
class RunProfileSpec:
    """Explicit, testable run-profile definition."""

    name: RunProfileName
    output_dir: RunPathName = RunPathName.WIKI_OUTPUT_DIR
    include_urls: bool = True
    debug_dir: RunPathName | None = None
    quality_report: bool = False
    error_report: bool = False

    def build_config(self, *, paths: RunPathConfig) -> RunConfig:
        from scrapers.base.run_config import RunConfig  # noqa: PLC0415

        return RunConfig(
            output_dir=paths.resolve(self.output_dir),
            include_urls=self.include_urls,
            debug_dir=(
                None if self.debug_dir is None else paths.resolve(self.debug_dir)
            ),
            quality_report=self.quality_report,
            error_report=self.error_report,
        )


RUN_PROFILE_SPECS: dict[RunProfileName, RunProfileSpec] = {
    RunProfileName.STRICT: RunProfileSpec(
        name=RunProfileName.STRICT,
        debug_dir=RunPathName.DEBUG_DIR,
        quality_report=True,
        error_report=False,
    ),
    RunProfileName.MINIMAL: RunProfileSpec(name=RunProfileName.MINIMAL),
    RunProfileName.DEBUG: RunProfileSpec(
        name=RunProfileName.DEBUG,
        debug_dir=RunPathName.DEBUG_DIR,
    ),
    RunProfileName.DEPRECATED: RunProfileSpec(
        name=RunProfileName.DEPRECATED,
        debug_dir=RunPathName.DEBUG_DIR,
    ),
}


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


def get_run_profile_spec(profile: RunProfileSelector) -> RunProfileSpec:
    """Return the explicit definition for a named profile."""
    normalized_profile = _coerce_profile(profile)
    spec = RUN_PROFILE_SPECS.get(normalized_profile)
    if spec is not None:
        return spec

    msg = f"Unsupported run profile: {normalized_profile!r}"
    raise ValueError(msg)


def build_run_profile(
    profile: RunProfileSelector,
    *,
    paths: RunPathConfig = DEFAULT_RUN_PATHS,
) -> RunConfig:
    """Build ``RunConfig`` for a named profile."""
    return get_run_profile_spec(profile).build_config(paths=paths)
