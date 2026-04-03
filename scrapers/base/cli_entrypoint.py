"""Shared CLI entrypoint helpers for scraper/export runner modules."""

from __future__ import annotations

import argparse
import dataclasses
import inspect
import warnings
from dataclasses import dataclass
from typing import TYPE_CHECKING

from scrapers.base.defaults import DEFAULT_ERROR_REPORT
from scrapers.base.defaults import DEFAULT_QUALITY_REPORT
from scrapers.base.logging import configure_logging
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
    return build_run_profile(RunProfileName.DEFAULT)


def complete_extractor_base_config() -> RunConfig:
    """Build canonical ``RunConfig`` for complete-extractor CLI modules."""
    return build_run_profile(RunProfileName.DEFAULT)


@dataclass(frozen=True)
class CliFlagSpec:
    name: str
    default: bool
    help_text: str
    justification: str
    review_by: str


def _validate_flag_catalog(flag_specs: tuple[CliFlagSpec, ...]) -> None:
    for spec in flag_specs:
        if not spec.justification.strip() or not spec.review_by.strip():
            msg = f"Flag {spec.name!r} must define justification and review_by (YAGNI)."
            raise ValueError(msg)


def _standard_flag_catalog(
    *,
    quality_report_default: bool,
    error_report_default: bool,
) -> tuple[CliFlagSpec, ...]:
    return (
        CliFlagSpec(
            name="quality-report",
            default=quality_report_default,
            help_text="Zapisz raport jakości do debug_dir/quality_report.json.",
            justification="Potrzebne do audytu jakości danych dla uruchomień produkcyjnych.",
            review_by="2026-12-31",
        ),
        CliFlagSpec(
            name="error-report",
            default=error_report_default,
            help_text="Zapisz raporty błędów do debug_dir/errors.jsonl.",
            justification="Ułatwia triage błędów bez ponawiania pełnego runu.",
            review_by="2026-12-31",
        ),
        CliFlagSpec(
            name="verbose",
            default=False,
            help_text="Ustaw poziom logów na INFO.",
            justification="Daje szybki podgląd postępu bez pełnego TRACE.",
            review_by="2026-12-31",
        ),
        CliFlagSpec(
            name="trace",
            default=False,
            help_text="Ustaw poziom logów na DEBUG (nadpisuje --verbose).",
            justification="Wymagane do debugowania parserów i dumpów technicznych.",
            review_by="2026-12-31",
        ),
    )


def build_standard_parser(
    *,
    quality_report_default: bool = DEFAULT_QUALITY_REPORT,
    error_report_default: bool = DEFAULT_ERROR_REPORT,
) -> argparse.ArgumentParser:
    """Build parser with standardized quality/error report flags."""
    parser = argparse.ArgumentParser()
    flag_specs = _standard_flag_catalog(
        quality_report_default=quality_report_default,
        error_report_default=error_report_default,
    )
    _validate_flag_catalog(flag_specs)

    for spec in flag_specs:
        parser.add_argument(
            f"--{spec.name}",
            action=argparse.BooleanOptionalAction if spec.name in {"quality-report", "error-report"} else "store_true",
            default=spec.default,
            help=spec.help_text,
        )
    return parser


def build_run_config(*, base_config: RunConfig, args: argparse.Namespace) -> RunConfig:
    """Build ``RunConfig`` from base profile and parsed CLI args."""
    return dataclasses.replace(
        base_config,
        quality_report=args.quality_report,
        error_report=args.error_report,
        verbose=args.verbose,
        trace=args.trace,
    )


def run_cli_entrypoint(
    *,
    target: Callable[..., None],
    base_config: RunConfig,
    argv: Sequence[str] | None = None,
    quality_report_default: bool = DEFAULT_QUALITY_REPORT,
    error_report_default: bool = DEFAULT_ERROR_REPORT,
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
    configure_logging(verbose=run_config.verbose, trace=run_config.trace)

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
