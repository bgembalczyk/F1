from bs4 import BeautifulSoup

from scrapers.engines.single_scraper import SingleEngineManufacturerScraper


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def test_single_engine_scraper_builds_infoboxes_and_filters_empty() -> None:
    scraper = SingleEngineManufacturerScraper()
    scraper.find_infoboxes = lambda soup: soup.find_all("table", class_="infobox")
    payload = scraper._build_infobox_payload(  # noqa: SLF001
        _soup(
            """
            <table class='infobox'><caption>Renault</caption></table>
            <table class='infobox'></table>
            """,
        ),
    )
    assert len(payload.data) == 1
    assert payload.data[0]["title"] == "Renault"


def test_single_engine_scraper_assembles_record_with_tables() -> None:
    scraper = SingleEngineManufacturerScraper()
    scraper.find_infoboxes = lambda soup: soup.find_all("table", class_="infobox")
    scraper.url = "https://example.com/engine"
    record = scraper._parse_soup(  # noqa: SLF001
        _soup(
            """
            <table class='wikitable'>
              <tr><th>Year</th><th>Power</th></tr>
              <tr><td>1986</td><td>900 hp</td></tr>
            </table>
            """,
        ),
    )[0]

    assert record["url"] == "https://example.com/engine"
    assert record["tables"][0]["headers"] == ["Year", "Power"]
