from scrapers.base.detail_url_resolver import resolve_first_valid_detail_url
from scrapers.base.detail_url_resolver import validate_detail_url
from scrapers.constructors.detail_url_resolver import ConstructorDetailUrlResolver
from scrapers.drivers.detail_url_resolver import DriverDetailUrlResolver
from scrapers.grands_prix.detail_url_resolver import GrandPrixDetailUrlResolver
from scrapers.seasons.detail_url_resolver import SeasonDetailUrlResolver


def test_validate_detail_url_rejects_empty_non_string_and_redlink() -> None:
    assert validate_detail_url(None) is None
    assert validate_detail_url(123) is None
    assert validate_detail_url("   ") is None
    assert (
        validate_detail_url(
            "https://en.wikipedia.org/w/index.php?title=Example&action=edit&redlink=1"
        )
        is None
    )


def test_validate_detail_url_accepts_trimmed_url() -> None:
    assert (
        validate_detail_url("  https://en.wikipedia.org/wiki/Ferrari  ")
        == "https://en.wikipedia.org/wiki/Ferrari"
    )


def test_resolve_first_valid_detail_url_supports_dotted_keys() -> None:
    record = {
        "constructor": {"url": "https://en.wikipedia.org/wiki/McLaren"},
        "constructor_url": "https://example.com/fallback",
    }
    assert (
        resolve_first_valid_detail_url(
            record,
            candidate_keys=("constructor.url", "constructor_url"),
        )
        == "https://en.wikipedia.org/wiki/McLaren"
    )


def test_constructor_resolver_checks_all_supported_keys() -> None:
    resolver = ConstructorDetailUrlResolver()

    assert (
        resolver.resolve({"constructor": {"url": "https://en.wikipedia.org/wiki/Williams"}})
        == "https://en.wikipedia.org/wiki/Williams"
    )
    assert (
        resolver.resolve({"constructor_url": "https://en.wikipedia.org/wiki/Kurtis_Kraft"})
        == "https://en.wikipedia.org/wiki/Kurtis_Kraft"
    )
    assert (
        resolver.resolve(
            {"team_url": "https://en.wikipedia.org/wiki/BMS_Scuderia_Italia"}
        )
        == "https://en.wikipedia.org/wiki/BMS_Scuderia_Italia"
    )


def test_domain_resolvers_have_consistent_api() -> None:
    assert (
        DriverDetailUrlResolver().resolve(
            {"driver": {"url": "https://en.wikipedia.org/wiki/Lewis_Hamilton"}}
        )
        == "https://en.wikipedia.org/wiki/Lewis_Hamilton"
    )
    assert (
        GrandPrixDetailUrlResolver().resolve(
            {"race_title": {"url": "https://en.wikipedia.org/wiki/British_Grand_Prix"}}
        )
        == "https://en.wikipedia.org/wiki/British_Grand_Prix"
    )
    assert (
        SeasonDetailUrlResolver().resolve(
            {"season": {"url": "https://en.wikipedia.org/wiki/2023_Formula_One_World_Championship"}}
        )
        == "https://en.wikipedia.org/wiki/2023_Formula_One_World_Championship"
    )
