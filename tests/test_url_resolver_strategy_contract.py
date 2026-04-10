from scrapers.url_resolver import DEFAULT_URL_RESOLVER_STRATEGY_REGISTRY


def test_wikipedia_strategy_resolves_relative_url_contract() -> None:
    resolved = DEFAULT_URL_RESOLVER_STRATEGY_REGISTRY.resolve_url(
        base_url="https://en.wikipedia.org/wiki/Lewis_Hamilton",
        href="/wiki/McLaren",
        domain="seasons",
    )

    assert resolved == "https://en.wikipedia.org/wiki/McLaren"


def test_wikipedia_strategy_resolves_section_alias_contract() -> None:
    aliases = DEFAULT_URL_RESOLVER_STRATEGY_REGISTRY.section_aliases_for(
        domain="seasons",
        section_id="results",
    )

    assert "results and standings" in {alias.lower() for alias in aliases}


def test_wikipedia_strategy_fallback_canonical_url_contract() -> None:
    fallback_url = DEFAULT_URL_RESOLVER_STRATEGY_REGISTRY.fallback_canonical_url(
        domain="seasons",
        base_url="https://en.wikipedia.org/wiki/2004_Formula_One_World_Championship",
        year="2005",
        season_page_title="2005_Formula_One_World_Championship",
    )

    assert fallback_url == "https://en.wikipedia.org/wiki/2005_Formula_One_World_Championship"
