from __future__ import annotations

import pytest

from scrapers.run_profiles import PROFILE_RESOLVER
from scrapers.run_profiles import RunProfileName
from scrapers.run_profiles import get_cli_profile_defaults
from scrapers.run_profiles import get_run_profile_spec
from scrapers.run_profiles import resolve_cli_profile


def test_cli_profile_resolver_accepts_canonical_names() -> None:
    assert resolve_cli_profile("default") is RunProfileName.DEFAULT
    assert resolve_cli_profile("debug") is RunProfileName.DEBUG


def test_cli_profile_defaults_follow_canonical_run_profiles() -> None:
    assert get_cli_profile_defaults("default") == (False, False)
    assert get_cli_profile_defaults("debug") == (False, False)


@pytest.mark.parametrize("legacy_profile", ["list_scraper", "complete_extractor"])
def test_profile_resolver_rejects_legacy_aliases_with_clear_error(
    legacy_profile: str,
) -> None:
    with pytest.raises(ValueError, match="not a valid RunProfileName"):
        PROFILE_RESOLVER.resolve_cli_profile(legacy_profile)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="not a valid RunProfileName"):
        resolve_cli_profile(legacy_profile)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="not a valid RunProfileName"):
        get_cli_profile_defaults(legacy_profile)  # type: ignore[arg-type]


def test_profile_resolver_rejects_invalid_profile_names() -> None:
    with pytest.raises(ValueError, match="not a valid RunProfileName"):
        PROFILE_RESOLVER.resolve_cli_profile("not-a-profile")  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="not a valid RunProfileName"):
        get_run_profile_spec("not-a-profile")  # type: ignore[arg-type]
