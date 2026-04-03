from __future__ import annotations

import argparse
import inspect
import warnings
from pathlib import Path
from typing import TYPE_CHECKING

from scrapers.base.cli_entrypoint import build_run_config
from scrapers.base.cli_entrypoint import build_standard_parser
from scrapers.base.run_profiles import LEGACY_CLI_PROFILE_NAMES
from scrapers.base.run_profiles import LegacyCliProfileName
from scrapers.base.run_profiles import get_cli_profile_defaults
from scrapers.cli.deprecation import deprecated_runtime_message
from scrapers.cli.legacy_registry import LEGACY_MODULE_REGISTRY
from scrapers.cli.legacy_registry import MODULE_DEFINITIONS
from scrapers.cli.legacy_registry import SCRAPER_REGISTRY

if TYPE_CHECKING:
    from collections.abc import Callable

from scrapers.base.run_config import RunConfig


def invoke_target(target: Callable[..., None], run_config: RunConfig) -> None:
    signature = inspect.signature(target)
    if "run_config" in signature.parameters:
        target(run_config=run_config)
        return
    target()


def _legacy_profile_choices() -> tuple[LegacyCliProfileName, ...]:
    return LEGACY_CLI_PROFILE_NAMES


def _build_profile_parser(
    default_profile: LegacyCliProfileName,
) -> argparse.ArgumentParser:
    profile_parser = argparse.ArgumentParser(add_help=False)
    profile_parser.add_argument(
        "--profile",
        choices=_legacy_profile_choices(),
        default=default_profile,
    )
    return profile_parser


def _parse_legacy_args(
    argv: list[str] | None,
    default_profile: LegacyCliProfileName,
) -> tuple[argparse.Namespace, argparse.Namespace]:
    profile_parser = _build_profile_parser(default_profile)
    profile_args, remaining = profile_parser.parse_known_args(argv)

    quality_default, error_default = get_cli_profile_defaults(profile_args.profile)
    parser = build_standard_parser(
        quality_report_default=quality_default,
        error_report_default=error_default,
    )
    args = parser.parse_args(remaining)
    return profile_args, args


def module_path_from_file(file_path: str) -> str:
    path = Path(file_path).resolve()
    suffixless_parts = path.with_suffix("").parts

    try:
        scrapers_index = suffixless_parts.index("scrapers")
    except ValueError as exc:
        msg = f"Cannot infer scrapers module path from {file_path!r}."
        raise ValueError(msg) from exc

    return ".".join(suffixless_parts[scrapers_index:])


def run_legacy_wrapper(
    module_path: str,
    argv: list[str] | None = None,
    *,
    invoke_target_fn: Callable[[Callable[..., None], RunConfig], None] = invoke_target,
) -> None:
    spec = SCRAPER_REGISTRY[module_path]
    definition = MODULE_DEFINITIONS[module_path]
    _, args = _parse_legacy_args(argv, spec.profile)
    run_config = build_run_config(base_config=spec.base_config, args=args)
    if definition.deprecated:
        warnings.warn(
            deprecated_runtime_message(
                module_path,
                replacement_module_path=definition.replacement_module_path,
            ),
            DeprecationWarning,
            stacklevel=2,
        )
    invoke_target_fn(spec.target, run_config)


def run_registered_module(module_path: str, argv: list[str] | None = None) -> None:
    """Run a legacy-compatible registered module command."""
    run_legacy_wrapper(module_path, argv)


def run_registered_module_for_caller(argv: list[str] | None = None) -> None:
    """Resolve caller module path and execute via command registry."""
    frame = inspect.currentframe()
    if frame is None or frame.f_back is None:
        msg = "Cannot infer caller module for legacy wrapper."
        raise RuntimeError(msg)

    try:
        caller_file = frame.f_back.f_code.co_filename
    finally:
        del frame

    run_registered_module(module_path_from_file(caller_file), argv)


def get_deprecated_module_migrations() -> tuple[tuple[str, str], ...]:
    migrations: list[tuple[str, str]] = []
    for definition in LEGACY_MODULE_REGISTRY.definitions:
        if not definition.deprecated:
            continue
        replacement = definition.replacement_module_path or definition.module_path
        migrations.append((definition.module_path, replacement))
    return tuple(migrations)
