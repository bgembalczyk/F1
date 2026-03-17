# ruff: noqa: PLR2004
from scrapers.base.helpers.config_factory import ScraperCommonConfig
from scrapers.base.helpers.config_factory import build_list_config
from scrapers.base.helpers.config_factory import build_list_scraper_options
from scrapers.base.helpers.config_factory import build_table_config
from scrapers.base.helpers.config_factory import build_table_scraper_options
from scrapers.base.options import ScraperOptions
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.scraper import F1TableScraper
from scrapers.circuits.list_scraper import CircuitsListScraper
from scrapers.drivers.list_scraper import F1DriversListScraper
from scrapers.grands_prix.list_scraper import GrandsPrixListScraper


class DummySourceAdapter:
    def __init__(self, html: str) -> None:
        self.html = html

    def get(self, _source: str | None = None, **_kwargs: object) -> str:
        return self.html


class DummyTableScraper(F1TableScraper):
    def _parse_soup(self, _soup):
        return []


class DummyStrictTableScraper(F1TableScraper):
    options_domain = "drivers"
    options_profile = "strict_seed"

    def _parse_soup(self, _soup):
        return []


def test_table_scraper_with_options():
    config = ScraperConfig(url="https://example.com")
    options = ScraperOptions(source_adapter=DummySourceAdapter("<html></html>"))

    scraper = DummyTableScraper(options=options, config=config)

    assert scraper.include_urls is True


def test_table_scraper_with_include_urls_option():
    config = ScraperConfig(url="https://example.com")
    options = ScraperOptions(
        include_urls=False,
        source_adapter=DummySourceAdapter("<html></html>"),
    )

    scraper = DummyTableScraper(options=options, config=config)

    assert scraper.include_urls is False


def test_build_table_config_applies_common_settings():
    options = build_table_config(
        config=ScraperCommonConfig(
            include_urls=False,
            normalize_empty_values=False,
            validation_mode="hard",
        ),
    )

    assert options.include_urls is False
    assert options.normalize_empty_values is False
    assert options.validation_mode == "hard"


def test_build_list_config_overrides_existing_options():
    base_options = ScraperOptions(
        include_urls=False,
        normalize_empty_values=False,
        validation_mode="hard",
    )

    options = build_list_config(
        options=base_options,
        config=ScraperCommonConfig(
            include_urls=True,
            normalize_empty_values=True,
            validation_mode="soft",
        ),
    )

    assert options is base_options
    assert options.include_urls is True
    assert options.normalize_empty_values is True
    assert options.validation_mode == "soft"


def test_build_table_scraper_options_uses_profile_and_domain_override():
    circuits_options = build_table_scraper_options(
        domain="circuits",
        profile="soft_seed",
    )
    assert circuits_options.include_urls is True
    assert circuits_options.normalize_empty_values is False
    assert circuits_options.validation_mode == "soft"

    drivers_options = build_table_scraper_options(
        domain="drivers",
        profile="strict_seed",
    )
    assert drivers_options.include_urls is True
    assert drivers_options.normalize_empty_values is False
    assert drivers_options.validation_mode == "hard"


def test_build_list_scraper_options_uses_profile():
    options = build_list_scraper_options(domain="constructors", profile="details")

    assert options.include_urls is True
    assert options.normalize_empty_values is True
    assert options.validation_mode == "soft"


def test_table_scraper_profile_applied_in_base_class():
    config = ScraperConfig(url="https://example.com")
    options = ScraperOptions(source_adapter=DummySourceAdapter("<html></html>"))

    scraper = DummyStrictTableScraper(options=options, config=config)

    assert scraper.include_urls is True
    assert scraper.normalize_empty_values is False
    assert scraper.validation_mode == "hard"


def test_list_scraper_profiles_keep_existing_defaults():
    source = DummySourceAdapter("<html></html>")

    circuits = CircuitsListScraper(options=ScraperOptions(source_adapter=source))
    assert circuits.include_urls is True
    assert circuits.normalize_empty_values is False
    assert circuits.validation_mode == "soft"

    grands_prix = GrandsPrixListScraper(options=ScraperOptions(source_adapter=source))
    assert grands_prix.include_urls is True
    assert grands_prix.normalize_empty_values is True
    assert grands_prix.validation_mode == "soft"


def test_extend_options_hook_keeps_custom_transformers_behavior():
    source = DummySourceAdapter("<html></html>")
    options = ScraperOptions(source_adapter=source)

    scraper = F1DriversListScraper(options=options)

    assert len(scraper.transformers) == 2
    assert (
        scraper.transformers[-1].__class__.__name__ == "DriversChampionshipsTransformer"
    )
