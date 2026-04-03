from __future__ import annotations

import pytest

from scrapers.base.run_profiles import LEGACY_CLI_PROFILE_NAMES
from scrapers.base.run_profiles import PROFILE_RESOLVER
from scrapers.base.run_profiles import RunProfileName
from scrapers.base.run_profiles import get_cli_profile_defaults
from scrapers.base.run_profiles import get_run_profile_spec
from scrapers.base.run_profiles import resolve_cli_profile
from scrapers.cli import _parse_legacy_args


def test_cli_profile_aliases_resolve_to_canonical_profiles() -> None:
    assert resolve_cli_profile("list_scraper") is RunProfileName.DEFAULT
    assert resolve_cli_profile("complete_extractor") is RunProfileName.DEFAULT


def test_cli_profile_defaults_follow_canonical_run_profiles() -> None:
    assert get_cli_profile_defaults("list_scraper") == (False, False)
    assert get_cli_profile_defaults("complete_extractor") == (False, False)


def test_legacy_arg_parser_uses_central_alias_choices_and_defaults() -> None:
    args = _parse_legacy_args([], _default_profile="list_scraper")

    assert LEGACY_CLI_PROFILE_NAMES == (
        "list_scraper",
        "complete_extractor",
    )
    assert args.quality_report is False
    assert args.error_report is False


def test_profile_resolver_contract_for_legacy_aliases() -> None:
    assert PROFILE_RESOLVER.resolve_cli_profile("list_scraper") is RunProfileName.DEFAULT
    assert PROFILE_RESOLVER.resolve_cli_profile(
        "complete_extractor",
    ) is RunProfileName.DEFAULT


def test_profile_resolver_rejects_invalid_profile_names() -> None:
    with pytest.raises(ValueError):
        PROFILE_RESOLVER.resolve_cli_profile("not-a-profile")  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        get_run_profile_spec("not-a-profile")  # type: ignore[arg-type]
