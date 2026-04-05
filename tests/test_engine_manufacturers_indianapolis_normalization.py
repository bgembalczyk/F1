from scrapers.base.options import ScraperOptions
from scrapers.engines.engine_manufacturers_list import EngineManufacturersListScraper


def test_indianapolis_record_normalization_embeds_url_into_manufacturer_link() -> None:
    scraper = EngineManufacturersListScraper(options=ScraperOptions(include_urls=True))

    normalized = scraper.normalize_indianapolis_record(
        {
            "manufacturer": "Cadillac",
            "manufacturer_url": "/wiki/Cadillac_in_Formula_One",
            "engines_built_in": [],
            "manufacturer_status": None,
            "seasons": [],
        },
    )

    assert normalized["manufacturer"] == {
        "text": "Cadillac",
        "url": "https://en.wikipedia.org/wiki/Cadillac_in_Formula_One",
    }
    assert "manufacturer_url" not in normalized


def test_indianapolis_record_normalization_omits_url_when_include_urls_disabled() -> (
    None
):
    scraper = EngineManufacturersListScraper(options=ScraperOptions(include_urls=False))

    normalized = scraper.normalize_indianapolis_record(
        {
            "manufacturer": "Cadillac",
            "manufacturer_url": "/wiki/Cadillac_in_Formula_One",
            "engines_built_in": [],
            "manufacturer_status": None,
            "seasons": [],
        },
    )

    assert normalized["manufacturer"] == {"text": "Cadillac", "url": None}
    assert "manufacturer_url" not in normalized
