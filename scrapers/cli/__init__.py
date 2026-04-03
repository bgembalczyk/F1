"""Backward-compatible shim for legacy `scrapers.cli` imports."""

from __future__ import annotations

from scrapers.cli.deprecation import DEPRECATION_POLICY
from scrapers.cli.deprecation import deprecated_runtime_message as _deprecated_runtime_message
from scrapers.cli.deprecation import render_deprecation_schedule_markdown
from scrapers.cli.dispatch import _parse_legacy_args
from scrapers.cli.dispatch import get_deprecated_module_migrations
from scrapers.cli.dispatch import invoke_target as _invoke_target
from scrapers.cli.dispatch import module_path_from_file as _module_path_from_file
from scrapers.cli.dispatch import run_registered_module
from scrapers.cli.dispatch import run_registered_module_for_caller
from scrapers.cli.legacy_registry import MODULE_DEFINITIONS
from scrapers.cli.main import _build_main_parser
from scrapers.cli.main import main
from scrapers.cli.main import run_wiki_cli


def run_legacy_wrapper(module_path: str, argv: list[str] | None = None) -> None:
    from scrapers.cli.dispatch import run_legacy_wrapper as _run_legacy_wrapper_impl

    _run_legacy_wrapper_impl(module_path, argv, invoke_target_fn=_invoke_target)


__all__ = [
    "DEPRECATION_POLICY",
    "MODULE_DEFINITIONS",
    "_build_main_parser",
    "_deprecated_runtime_message",
    "_parse_legacy_args",
    "_invoke_target",
    "_module_path_from_file",
    "get_deprecated_module_migrations",
    "main",
    "render_deprecation_schedule_markdown",
    "run_legacy_wrapper",
    "run_registered_module",
    "run_registered_module_for_caller",
    "run_wiki_cli",
]
