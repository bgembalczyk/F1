"""Points scraper contract tests."""

from scrapers.points.base_points_scraper import BasePointsScraper
from tests.support.refactored_base_classes_utils import POINTS_SYSTEMS_URL


def test_points_base_url_is_set() -> None:
    """Base points scraper URL remains stable."""
    assert BasePointsScraper.BASE_URL == POINTS_SYSTEMS_URL
