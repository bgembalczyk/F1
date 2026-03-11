from scrapers.base.helpers.config_factory import ScraperCommonConfig
from scrapers.base.helpers.config_factory import build_list_config
from scrapers.base.helpers.config_factory import build_table_config
from scrapers.base.options import ScraperOptions
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.scraper import F1TableScraper


class DummySourceAdapter:
    def __init__(self, html: str) -> None:
        self.html = html

    def get(self, source: str | None = None, **_kwargs: object) -> str:
        return self.html


class DummyTableScraper(F1TableScraper):
    def _parse_soup(self, soup):
        return []


def test_table_scraper_with_options():
    config = ScraperConfig(url="https://example.com")
    options = ScraperOptions(source_adapter=DummySourceAdapter("<html></html>"))

    scraper = DummyTableScraper(options=options, config=config)

    assert scraper.include_urls is True


def test_table_scraper_with_include_urls_option():
    config = ScraperConfig(url="https://example.com")
    options = ScraperOptions(
        include_urls=False, source_adapter=DummySourceAdapter("<html></html>"),
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
