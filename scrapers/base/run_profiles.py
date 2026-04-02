"""Central run-profile definitions used by scraper entrypoints."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import logging
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Literal

if TYPE_CHECKING:
    from scrapers.base.run_config import RunConfig

from scrapers.base.run_profile_contracts import BuildRunConfigRequestDTO
from scrapers.base.run_profile_contracts import BuildRunConfigResultDTO

_logger = logging.getLogger(__name__)


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


LegacyCliProfileName = Literal[
    "list_scraper",
    "complete_extractor",
    "deprecated_entrypoint",
]

RunProfileSelector = (
    RunProfileName
    | Literal[
        "strict",
        "minimal",
        "debug",
        "deprecated",
    ]
)

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
    cli_aliases: tuple[LegacyCliProfileName, ...] = ()

    def build_config(
        self,
        request: BuildRunConfigRequestDTO | None = None,
        *,
        paths: RunPathConfig | None = None,
    ) -> BuildRunConfigResultDTO:
        from scrapers.base.run_config import RunConfig

        request_dto = self._coerce_build_config_request(request=request, paths=paths)
        request_dto.validate()
        result = BuildRunConfigResultDTO(
            run_config=RunConfig(
                output_dir=request_dto.paths.resolve(self.output_dir),
                include_urls=self.include_urls,
                debug_dir=(
                    None
                    if self.debug_dir is None
                    else request_dto.paths.resolve(self.debug_dir)
                ),
                quality_report=self.quality_report,
                error_report=self.error_report,
            ),
        )
        result.validate()
        _logger.info(
            "run profile build_config: %s -> %s",
            request_dto.short(),
            result.short(),
        )
        return result

    def _coerce_build_config_request(
        self,
        *,
        request: BuildRunConfigRequestDTO | None,
        paths: RunPathConfig | None,
    ) -> BuildRunConfigRequestDTO:
        if request is not None:
            return request
        if paths is None:
            msg = "Either request DTO or paths must be provided"
            raise TypeError(msg)
        return BuildRunConfigRequestDTO(paths=paths)


RUN_PROFILE_SPECS: dict[RunProfileName, RunProfileSpec] = {
    RunProfileName.STRICT: RunProfileSpec(
        name=RunProfileName.STRICT,
        debug_dir=RunPathName.DEBUG_DIR,
        quality_report=True,
        error_report=False,
        cli_aliases=("list_scraper",),
    ),
    RunProfileName.MINIMAL: RunProfileSpec(
        name=RunProfileName.MINIMAL,
        cli_aliases=("complete_extractor",),
    ),
    RunProfileName.DEBUG: RunProfileSpec(
        name=RunProfileName.DEBUG,
        debug_dir=RunPathName.DEBUG_DIR,
    ),
    RunProfileName.DEPRECATED: RunProfileSpec(
        name=RunProfileName.DEPRECATED,
        debug_dir=RunPathName.DEBUG_DIR,
        cli_aliases=("deprecated_entrypoint",),
    ),
}


LEGACY_CLI_PROFILE_ALIASES: dict[LegacyCliProfileName, RunProfileName] = {
    alias: spec.name
    for spec in RUN_PROFILE_SPECS.values()
    for alias in spec.cli_aliases
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
    result = PROFILE_RESOLVER.validate_supported_profile(normalized_profile).build_config(
        BuildRunConfigRequestDTO(paths=paths),
    )
    return result.run_config
