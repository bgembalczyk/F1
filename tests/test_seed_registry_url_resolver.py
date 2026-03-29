import pytest

from layers.seed.registry.url_resolver import resolve_scraper_url


class _Config:
    url = "https://example.test/config"


class _ConfigBasedScraper:
    CONFIG = _Config()


class _LegacyScraper:
    url = "https://example.test/legacy"


class _InvalidScraper:
    pass


def test_resolve_scraper_url_prefers_config_contract() -> None:
    assert resolve_scraper_url(_ConfigBasedScraper) == "https://example.test/config"


def test_resolve_scraper_url_supports_legacy_url_attribute() -> None:
    assert resolve_scraper_url(_LegacyScraper) == "https://example.test/legacy"


def test_resolve_scraper_url_raises_when_missing_metadata() -> None:
    with pytest.raises(AttributeError, match="does not expose scraper URL"):
        resolve_scraper_url(_InvalidScraper)
