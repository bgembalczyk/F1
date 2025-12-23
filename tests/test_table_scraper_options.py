import warnings

import pytest

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


def test_table_scraper_options_without_legacy_params_has_no_warning() -> None:
    config = ScraperConfig(url="https://example.com")
    options = ScraperOptions(source_adapter=DummySourceAdapter("<html></html>"))

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        DummyTableScraper(options=options, config=config)

    assert not any(issubclass(item.category, DeprecationWarning) for item in caught)


def test_table_scraper_legacy_params_emit_warning_and_set_options() -> None:
    config = ScraperConfig(url="https://example.com")

    with pytest.warns(DeprecationWarning, match="Parametry include_urls"):
        scraper = DummyTableScraper(config=config, include_urls=False)

    assert scraper.include_urls is False
