from bs4 import BeautifulSoup

from scrapers.base.helpers.tables.lap_records import LapRecordsTableScraper
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.headers import normalize_header
from scrapers.base.table.pipeline import TablePipeline


def test_normalize_header_consistent_between_pipeline_and_lap_records() -> None:
    header = " Time "
    expected = normalize_header(header)

    soup = BeautifulSoup("<td>1:23.456</td>", "html.parser")
    cell = soup.find("td")
    assert cell is not None

    pipeline = TablePipeline(
        config=ScraperConfig(url="https://example.com"),
        include_urls=False,
        skip_sentinel=object(),
    )
    key, _, _ = pipeline._normalize_cell(header, cell)

    assert key == expected

    lap_scraper = LapRecordsTableScraper()
    assert lap_scraper.headers_match([header]) is True
    assert normalize_header("Time") == expected
