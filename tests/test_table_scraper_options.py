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
        include_urls=False, source_adapter=DummySourceAdapter("<html></html>")
    )

    scraper = DummyTableScraper(options=options, config=config)

    assert scraper.include_urls is False
