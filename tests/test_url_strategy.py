from scrapers.base.helpers.url import DefaultUrlStrategy


def test_url_strategy_resolves_relative_url() -> None:
    strategy = DefaultUrlStrategy()

    assert (
        strategy.canonicalize("https://en.wikipedia.org/wiki/Foo", "/wiki/Bar")
        == "https://en.wikipedia.org/wiki/Bar"
    )


def test_url_strategy_resolves_schema_relative_url() -> None:
    strategy = DefaultUrlStrategy()

    assert (
        strategy.canonicalize("https://en.wikipedia.org/wiki/Foo", "//host/path")
        == "https://host/path"
    )


def test_url_strategy_rejects_invalid_url() -> None:
    strategy = DefaultUrlStrategy()

    assert strategy.canonicalize("https://en.wikipedia.org/wiki/Foo", "mailto:test@example.com") is None


def test_url_strategy_fallbacks_to_https_for_schema_relative_base_without_scheme() -> None:
    strategy = DefaultUrlStrategy()

    assert strategy.resolve_relative("en.wikipedia.org/wiki/Foo", "//host/path") == "https://host/path"
