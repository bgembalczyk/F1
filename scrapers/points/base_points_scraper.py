"""Base scraper for points scoring systems."""
from scrapers.base.table.scraper import F1TableScraper


class BasePointsScraper(F1TableScraper):
    """
    Base class for points scoring systems scrapers.
    
    Provides common URL for all points scoring system tables from the same Wikipedia page.
    
    Subclasses should define their own CONFIG with specific:
    - section_id (specific section within the page)
    - expected_headers
    - schema
    - record_factory
    """
    
    # All points scoring scrapers use the same Wikipedia page
    BASE_URL = "https://en.wikipedia.org/wiki/List_of_Formula_One_World_Championship_points_scoring_systems"
