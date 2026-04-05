import pytest

from scrapers.base.options import ScraperOptions
from scrapers.circuits.list_scraper import CircuitsListScraper
from scrapers.drivers.list_scraper import F1DriversListScraper


class StubFetcher:
    def __init__(self, html: str) -> None:
        self.html = html
        self.calls = 0

    def get_text(self, _url: str, *, _timeout: int | None = None) -> str:
        self.calls += 1
        return self.html

    def get(self, url: str) -> str:
        return self.get_text(url)


pytest.importorskip("bs4")


@pytest.mark.parametrize(
    "scraper_cls",
    [
        F1DriversListScraper,
        CircuitsListScraper,
    ],
)
def test_minimal_fetch_contract(scraper_cls, minimal_fetch_html) -> None:
    fetcher = StubFetcher(minimal_fetch_html)
    scraper = scraper_cls(options=ScraperOptions(fetcher=fetcher, include_urls=True))

    data = scraper.get_data()

    assert fetcher.calls == 1
    assert isinstance(data, list)
    assert data
    assert all(isinstance(record, dict) for record in data)
