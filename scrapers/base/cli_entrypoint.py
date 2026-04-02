"""Shared CLI entrypoint helpers for scraper/export runner modules."""

from __future__ import annotations

import argparse
import dataclasses
import inspect
import warnings
from typing import TYPE_CHECKING

from scrapers.base.logging import configure_logging
from scrapers.base.debug_contract import DebugMode
from scrapers.base.run_profiles import RunProfileName
from scrapers.base.run_profiles import build_run_profile
from scrapers.base.run_profiles import get_cli_profile_defaults
from scrapers.base.run_profiles import resolve_cli_profile

if TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Sequence

    from scrapers.base.constants import CliMainProfile
    from scrapers.base.run_config import RunConfig


def deprecated_module_base_config() -> RunConfig:
    """Build canonical ``RunConfig`` for deprecated compatibility modules."""
    return build_run_profile(RunProfileName.DEPRECATED)


def complete_extractor_base_config() -> RunConfig:
    """Build canonical ``RunConfig`` for complete-extractor CLI modules."""
    return build_run_profile(RunProfileName.MINIMAL)


def build_standard_parser(
    *,
    quality_report_default: bool = False,
    error_report_default: bool = False,
    debug_mode_default: DebugMode = DebugMode.OFF,
) -> argparse.ArgumentParser:
    """Build parser with standardized quality/error report flags."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--quality-report",
        action=argparse.BooleanOptionalAction,
        default=quality_report_default,
        help="Zapisz raport jakości do debug_dir/quality_report.json.",
    )
    parser.add_argument(
        "--error-report",
        action=argparse.BooleanOptionalAction,
        default=error_report_default,
        help="Zapisz raporty błędów do debug_dir/errors.jsonl.",
    )
    parser.add_argument(
        "--debug-mode",
        choices=tuple(mode.value for mode in DebugMode),
        default=debug_mode_default.value,
        help="Tryb debug: off=WARNING, verbose=INFO, trace=DEBUG+dumpy.",
    )
    return parser


def build_run_config(*, base_config: RunConfig, args: argparse.Namespace) -> RunConfig:
    """Build ``RunConfig`` from base profile and parsed CLI args."""
    return dataclasses.replace(
        base_config,
        quality_report=args.quality_report,
        error_report=args.error_report,
        debug_mode=DebugMode(args.debug_mode),
    )


def run_cli_entrypoint(
    *,
    target: Callable[..., None],
    base_config: RunConfig,
    argv: Sequence[str] | None = None,
    quality_report_default: bool = False,
    error_report_default: bool = False,
    deprecation_message: str | None = None,
    deprecation_stacklevel: int = 2,
) -> None:
    """Parse standardized args, create ``RunConfig``, and invoke target."""
    parser = build_standard_parser(
        quality_report_default=quality_report_default,
        error_report_default=error_report_default,
        debug_mode_default=base_config.debug_mode,
    )
    args = parser.parse_args(argv)
    run_config = build_run_config(base_config=base_config, args=args)
    configure_logging(debug_mode=run_config.debug_mode)

    if deprecation_message:
        warnings.warn(
            deprecation_message,
            DeprecationWarning,
            stacklevel=deprecation_stacklevel,
        )

    _invoke_target(target=target, run_config=run_config)


def build_cli_main(
    *,
    target: Callable[..., None],
    base_config: RunConfig,
    profile: CliMainProfile | str,
    argv: Sequence[str] | None = None,
    quality_report_default: bool | None = None,
    error_report_default: bool | None = None,
    deprecation_message: str | None = None,
    deprecation_stacklevel: int = 2,
) -> Callable[[], None]:
    """Build reusable ``__main__`` launcher with standardized profile defaults."""
    normalized_profile = resolve_cli_profile(profile)
    profile_quality_default, profile_error_default = get_cli_profile_defaults(
        normalized_profile,
    )
    quality_default = (
        profile_quality_default
        if quality_report_default is None
        else quality_report_default
    )
    error_default = (
        profile_error_default if error_report_default is None else error_report_default
    )

    def _main() -> None:
        run_cli_entrypoint(
            target=target,
            base_config=base_config,
            argv=argv,
            quality_report_default=quality_default,
            error_report_default=error_default,
            deprecation_message=deprecation_message,
            deprecation_stacklevel=deprecation_stacklevel,
        )

    return _main


def build_complete_extractor_main(
    *,
    target: Callable[..., None],
    argv: Sequence[str] | None = None,
) -> Callable[[], None]:
    """Backward-compatible helper for complete extractor entrypoints."""
    return build_cli_main(
        target=target,
        base_config=complete_extractor_base_config(),
        profile="complete_extractor",
        argv=argv,
    )


def build_deprecated_module_main(
    *,
    target: Callable[..., None],
    deprecation_message: str,
    argv: Sequence[str] | None = None,
) -> Callable[[], None]:
    """Backward-compatible helper for deprecated entrypoints."""
    return build_cli_main(
        target=target,
        base_config=deprecated_module_base_config(),
        profile="deprecated_entrypoint",
        argv=argv,
        deprecation_message=deprecation_message,
        deprecation_stacklevel=3,
    )


def _invoke_target(*, target: Callable[..., None], run_config: RunConfig) -> None:
    try:
        signature = inspect.signature(target)
    except (TypeError, ValueError):
        target()
        return

    if "run_config" in signature.parameters:
        target(run_config=run_config)
        return

    target()
