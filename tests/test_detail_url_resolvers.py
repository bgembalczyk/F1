from scrapers.base.detail_url_resolver import CircuitDetailUrlResolver
from scrapers.base.detail_url_resolver import ConstructorDetailUrlResolver
from scrapers.base.detail_url_resolver import DriverDetailUrlResolver
from scrapers.base.detail_url_resolver import GrandPrixDetailUrlResolver
from scrapers.base.detail_url_resolver import SeasonDetailUrlResolver


def test_driver_detail_url_resolver_prefers_driver_link_url() -> None:
    resolver = DriverDetailUrlResolver()
    record = {
        "driver": {
            "text": "Lewis Hamilton",
            "url": "https://en.wikipedia.org/wiki/Lewis_Hamilton",
        },
    }
    assert resolver.resolve(record) == "https://en.wikipedia.org/wiki/Lewis_Hamilton"


def test_driver_detail_url_resolver_returns_none_for_invalid_shape() -> None:
    resolver = DriverDetailUrlResolver()
    assert resolver.resolve({"driver": "Lewis Hamilton"}) is None


def test_constructor_detail_url_resolver_uses_constructor_link_url() -> None:
    resolver = ConstructorDetailUrlResolver()
    record = {
        "constructor": {
            "text": "Ferrari",
            "url": "https://en.wikipedia.org/wiki/Scuderia_Ferrari",
        },
    }
    assert resolver.resolve(record) == "https://en.wikipedia.org/wiki/Scuderia_Ferrari"


def test_constructor_detail_url_resolver_falls_back_to_constructor_url() -> None:
    resolver = ConstructorDetailUrlResolver()
    record = {
        "constructor": "Kurtis Kraft",
        "constructor_url": "https://en.wikipedia.org/wiki/Kurtis_Kraft",
    }
    assert resolver.resolve(record) == "https://en.wikipedia.org/wiki/Kurtis_Kraft"


def test_constructor_detail_url_resolver_falls_back_to_team_url() -> None:
    resolver = ConstructorDetailUrlResolver()
    record = {
        "team": "BMS Scuderia Italia",
        "team_url": "https://en.wikipedia.org/wiki/BMS_Scuderia_Italia",
    }
    assert resolver.resolve(record) == "https://en.wikipedia.org/wiki/BMS_Scuderia_Italia"


def test_constructor_detail_url_resolver_skips_redlinks() -> None:
    resolver = ConstructorDetailUrlResolver()
    redlink = (
        "https://en.wikipedia.org/w/index.php?title=Ecurie_Bleue"
        "&action=edit&redlink=1"
    )

    assert resolver.resolve({"constructor": {"url": redlink}}) is None
    assert resolver.resolve({"constructor_url": redlink}) is None
    assert resolver.resolve({"team_url": redlink}) is None


def test_circuit_detail_url_resolver_reads_circuit_url() -> None:
    resolver = CircuitDetailUrlResolver()
    record = {
        "circuit": {
            "text": "Monza Circuit",
            "url": "https://en.wikipedia.org/wiki/Monza_Circuit",
        },
    }
    assert resolver.resolve(record) == "https://en.wikipedia.org/wiki/Monza_Circuit"


def test_season_detail_url_resolver_reads_season_url() -> None:
    resolver = SeasonDetailUrlResolver()
    record = {
        "season": {
            "text": "2024 Formula One World Championship",
            "url": "https://en.wikipedia.org/wiki/2024_Formula_One_World_Championship",
        },
    }
    assert (
        resolver.resolve(record)
        == "https://en.wikipedia.org/wiki/2024_Formula_One_World_Championship"
    )


def test_grand_prix_detail_url_resolver_reads_race_title_url() -> None:
    resolver = GrandPrixDetailUrlResolver()
    record = {
        "race_title": {
            "text": "British Grand Prix",
            "url": "https://en.wikipedia.org/wiki/British_Grand_Prix",
        },
    }
    assert resolver.resolve(record) == "https://en.wikipedia.org/wiki/British_Grand_Prix"
