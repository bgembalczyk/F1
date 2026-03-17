"""Shared CLI entrypoint helpers for scraper/export runner modules."""

from __future__ import annotations

import argparse
import dataclasses
import inspect
import warnings
from collections.abc import Callable
from collections.abc import Sequence
from pathlib import Path
from typing import Literal

from scrapers.base.run_config import RunConfig

CliMainProfile = Literal[
    "list_scraper",
    "complete_extractor",
    "deprecated_entrypoint",
]


_PROFILE_DEFAULTS: dict[CliMainProfile, tuple[bool, bool]] = {
    "list_scraper": (True, False),
    "complete_extractor": (False, False),
    "deprecated_entrypoint": (True, False),
}

DEFAULT_WIKI_OUTPUT_DIR = Path("../../data/wiki")
DEFAULT_DEBUG_DIR = Path("../../data/debug")


def deprecated_module_base_config() -> RunConfig:
    """Build canonical ``RunConfig`` for deprecated compatibility modules."""
    return RunConfig(
        output_dir=DEFAULT_WIKI_OUTPUT_DIR,
        include_urls=True,
        debug_dir=DEFAULT_DEBUG_DIR,
    )


def complete_extractor_base_config() -> RunConfig:
    """Build canonical ``RunConfig`` for complete-extractor CLI modules."""
    return RunConfig(output_dir=DEFAULT_WIKI_OUTPUT_DIR)


def build_standard_parser(
    *,
    quality_report_default: bool = False,
    error_report_default: bool = False,
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
    return parser


def build_run_config(*, base_config: RunConfig, args: argparse.Namespace) -> RunConfig:
    """Build ``RunConfig`` from base profile and parsed CLI args."""
    return dataclasses.replace(
        base_config,
        quality_report=args.quality_report,
        error_report=args.error_report,
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
    )
    args = parser.parse_args(argv)
    run_config = build_run_config(base_config=base_config, args=args)

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
    profile: CliMainProfile,
    argv: Sequence[str] | None = None,
    quality_report_default: bool | None = None,
    error_report_default: bool | None = None,
    deprecation_message: str | None = None,
    deprecation_stacklevel: int = 2,
) -> Callable[[], None]:
    """Build reusable ``__main__`` launcher with standardized profile defaults."""
    profile_quality_default, profile_error_default = _PROFILE_DEFAULTS[profile]
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


def build_deprecated_module_main(
    *,
    target: Callable[..., None],
    deprecation_message: str,
    argv: Sequence[str] | None = None,
    base_config: RunConfig | None = None,
    deprecation_stacklevel: int = 2,
) -> Callable[[], None]:
    """Build ``__main__`` launcher dedicated to deprecated module shims."""
    return build_cli_main(
        target=target,
        base_config=base_config or deprecated_module_base_config(),
        profile="deprecated_entrypoint",
        argv=argv,
        deprecation_message=deprecation_message,
        deprecation_stacklevel=deprecation_stacklevel,
    )


def build_complete_extractor_main(
    *,
    target: Callable[..., None],
    argv: Sequence[str] | None = None,
    base_config: RunConfig | None = None,
) -> Callable[[], None]:
    """Build ``__main__`` launcher for complete extractor modules."""
    return build_cli_main(
        target=target,
        base_config=base_config or complete_extractor_base_config(),
        profile="complete_extractor",
        argv=argv,
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


__all__ = [
    "CliMainProfile",
    "build_cli_main",
    "build_complete_extractor_main",
    "build_deprecated_module_main",
    "build_run_config",
    "build_standard_parser",
    "complete_extractor_base_config",
    "deprecated_module_base_config",
    "run_cli_entrypoint",
]
