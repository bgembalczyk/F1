"""Base scraper for points scoring systems."""

from scrapers.scraper_table import F1TableScraper
from scrapers.source_catalog import POINTS_SCORING_SYSTEMS


class BasePointsScraper(F1TableScraper):
    """
    Base class for points scoring systems scrapers.

    Provides common URL for all points scoring system tables
    from the same Wikipedia page.

    Subclasses should define their own CONFIG with specific:
    - section_id (specific section within the page)
    - expected_headers
    - schema
    - record_factory
    """

    # All points scoring scrapers use the same Wikipedia page
    BASE_URL = POINTS_SCORING_SYSTEMS.base_url
