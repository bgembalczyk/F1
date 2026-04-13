"""Points scraper contract tests."""

from scrapers.points_scraper import PointsScraper
from scrapers.source_catalog import POINTS_SCORING_SYSTEMS


def test_points_base_url_is_set() -> None:
    """Points scraper URL remains stable."""
    assert PointsScraper.BASE_URL == POINTS_SCORING_SYSTEMS.base_url
