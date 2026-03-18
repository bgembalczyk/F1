from __future__ import annotations

from scrapers.base.run_profiles import LEGACY_CLI_PROFILE_NAMES
from scrapers.base.run_profiles import RunProfileName
from scrapers.base.run_profiles import get_cli_profile_defaults
from scrapers.base.run_profiles import resolve_cli_profile
from scrapers.cli import _parse_legacy_args


def test_cli_profile_aliases_resolve_to_canonical_profiles() -> None:
    assert resolve_cli_profile("list_scraper") is RunProfileName.STRICT
    assert resolve_cli_profile("complete_extractor") is RunProfileName.MINIMAL
    assert resolve_cli_profile("deprecated_entrypoint") is RunProfileName.DEPRECATED


def test_cli_profile_defaults_follow_canonical_run_profiles() -> None:
    assert get_cli_profile_defaults("list_scraper") == (True, False)
    assert get_cli_profile_defaults("complete_extractor") == (False, False)
    assert get_cli_profile_defaults("deprecated_entrypoint") == (False, False)


def test_legacy_arg_parser_uses_central_alias_choices_and_defaults() -> None:
    profile_args, args = _parse_legacy_args([], default_profile="list_scraper")

    assert LEGACY_CLI_PROFILE_NAMES == (
        "list_scraper",
        "complete_extractor",
        "deprecated_entrypoint",
    )
    assert profile_args.profile == "list_scraper"
    assert args.quality_report is True
    assert args.error_report is False
