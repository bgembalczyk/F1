import pytest

from scrapers.base.options import ScraperOptions


def test_scraper_options_rejects_non_positive_timeout():
    with pytest.raises(ValueError):
        ScraperOptions(timeout=0)

    with pytest.raises(ValueError):
        ScraperOptions(timeout=-1)


def test_scraper_options_rejects_negative_retries():
    with pytest.raises(ValueError):
        ScraperOptions(retries=-1)
