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
    DEFAULT = "default"
    DEBUG = "debug"


class RunPathName(str, Enum):
    WIKI_OUTPUT_DIR = "wiki_output_dir"
    DEBUG_DIR = "debug_dir"


LegacyCliProfileName = Literal[
    "list_scraper",
    "complete_extractor",
]

RunProfileSelector = RunProfileName | Literal["default", "debug"]

CliProfileSelector = RunProfileSelector | LegacyCliProfileName


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
        from scrapers.base.run_config import RunConfig

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
    RunProfileName.DEFAULT: RunProfileSpec(
        name=RunProfileName.DEFAULT,
    ),
    RunProfileName.DEBUG: RunProfileSpec(
        name=RunProfileName.DEBUG,
        debug_dir=RunPathName.DEBUG_DIR,
    ),
}


LEGACY_CLI_PROFILE_ALIASES: dict[LegacyCliProfileName, RunProfileName] = {
    "list_scraper": RunProfileName.DEFAULT,
    "complete_extractor": RunProfileName.DEFAULT,
}

LEGACY_CLI_PROFILE_NAMES: tuple[LegacyCliProfileName, ...] = tuple(
    LEGACY_CLI_PROFILE_ALIASES,
)


@dataclass(frozen=True)
class ProfileResolver:
    """Normalize, validate and resolve canonical/legacy profile names."""

    legacy_cli_aliases: dict[LegacyCliProfileName, RunProfileName]

    def _normalize_profile(self, profile: RunProfileSelector) -> RunProfileName:
        if isinstance(profile, RunProfileName):
            return profile
        return RunProfileName(profile)

    def _coerce_profile(self, profile: RunProfileSelector) -> RunProfileName:
        return self._normalize_profile(profile)

    def resolve_cli_profile(self, profile: CliProfileSelector) -> RunProfileName:
        if isinstance(profile, RunProfileName):
            return profile
        if profile in self.legacy_cli_aliases:
            return self.legacy_cli_aliases[profile]
        return self._normalize_profile(profile)

    def validate_supported_profile(self, profile: RunProfileName) -> RunProfileSpec:
        spec = RUN_PROFILE_SPECS.get(profile)
        if spec is not None:
            return spec

        msg = f"Unsupported run profile: {profile!r}"
        raise ValueError(msg)


PROFILE_RESOLVER = ProfileResolver(legacy_cli_aliases=LEGACY_CLI_PROFILE_ALIASES)


def resolve_cli_profile(profile: CliProfileSelector) -> RunProfileName:
    """Resolve canonical and legacy CLI profile names to a run profile."""
    return PROFILE_RESOLVER.resolve_cli_profile(profile)


def get_run_profile_spec(profile: RunProfileSelector) -> RunProfileSpec:
    """Return the explicit definition for a named profile."""
    normalized_profile = PROFILE_RESOLVER._coerce_profile(profile)
    return PROFILE_RESOLVER.validate_supported_profile(normalized_profile)


def get_cli_profile_defaults(profile: CliProfileSelector) -> tuple[bool, bool]:
    """Return default quality/error flags for canonical or legacy CLI profiles."""
    spec = get_run_profile_spec(resolve_cli_profile(profile))
    return spec.quality_report, spec.error_report


def build_run_profile(
    profile: RunProfileSelector,
    *,
    paths: RunPathConfig = DEFAULT_RUN_PATHS,
) -> RunConfig:
    """Build ``RunConfig`` for a named profile."""
    normalized_profile = PROFILE_RESOLVER._coerce_profile(profile)
    return PROFILE_RESOLVER.validate_supported_profile(normalized_profile).build_config(
        paths=paths,
    )
