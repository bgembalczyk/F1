import pytest

from scrapers.circuits_list_scraper import CircuitsListScraper
from scrapers.list_scraper_drivers import F1DriversListScraper
from scrapers.options import ScraperOptions
from tests.contract.dummy_classes import StubFetcher

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
