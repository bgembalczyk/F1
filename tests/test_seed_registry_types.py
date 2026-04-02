import pytest

from layers.seed.registry.types import DomainName
from layers.seed.registry.types import RunProfile
from layers.seed.registry.types import SeedName
from layers.seed.registry.types import parse_domain_name
from layers.seed.registry.types import parse_run_profile
from layers.seed.registry.types import parse_seed_name


def test_parse_seed_name_returns_enum() -> None:
    assert parse_seed_name("drivers") is SeedName.DRIVERS


def test_parse_seed_name_raises_readable_error() -> None:
    with pytest.raises(ValueError, match="Unsupported seed_name 'unknown_seed'"):
        parse_seed_name("unknown_seed")


def test_parse_domain_name_returns_enum() -> None:
    assert parse_domain_name("grands_prix") is DomainName.GRANDS_PRIX


def test_parse_domain_name_raises_readable_error() -> None:
    with pytest.raises(ValueError, match="Unsupported domain 'unknown_domain'"):
        parse_domain_name("unknown_domain")


def test_parse_run_profile_returns_enum() -> None:
    assert parse_run_profile("debug") is RunProfile.DEBUG


def test_parse_run_profile_raises_readable_error() -> None:
    with pytest.raises(ValueError, match="Unsupported run profile 'nightly'"):
        parse_run_profile("nightly")
