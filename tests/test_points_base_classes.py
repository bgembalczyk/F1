"""Points scraper contract tests."""

import pytest

from scrapers.points.base_points_scraper import BasePointsScraper
from scrapers.points.points_scoring_systems_history import (
    PointsScoringSystemsHistoryScraper,
)
from scrapers.points.shortened_race_points import ShortenedRacePointsScraper
from scrapers.points.sprint_qualifying_points import SprintQualifyingPointsScraper
from tests.support.refactored_base_classes_utils import (
    POINTS_SYSTEMS_URL,
    assert_issubclass_cases,
)


@pytest.mark.parametrize(
    ("child", "parent"),
    [
        (SprintQualifyingPointsScraper, BasePointsScraper),
        (ShortenedRacePointsScraper, BasePointsScraper),
        (PointsScoringSystemsHistoryScraper, BasePointsScraper),
    ],
)
def test_points_scraper_inheritance(child: type, parent: type) -> None:
    """All points scrapers inherit from the same base class."""
    assert_issubclass_cases([(child, parent)])


def test_points_base_url_is_set() -> None:
    """Base points scraper URL remains stable."""
    assert BasePointsScraper.BASE_URL == POINTS_SYSTEMS_URL


@pytest.mark.parametrize(
    "scraper_cls",
    [
        SprintQualifyingPointsScraper,
        ShortenedRacePointsScraper,
        PointsScoringSystemsHistoryScraper,
    ],
)
def test_points_scrapers_use_base_url(scraper_cls: type) -> None:
    """Derived points scrapers should reuse the base URL."""
    assert scraper_cls.CONFIG.url == BasePointsScraper.BASE_URL
