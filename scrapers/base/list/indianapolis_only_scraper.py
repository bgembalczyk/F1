"""Base scraper for Indianapolis 500 only lists."""

from scrapers.base.list.scraper import F1ListScraper


class IndianapolisOnlyListScraper(F1ListScraper):
    """
    Base class for Indianapolis 500 only list scrapers.

    This class provides common configuration for scraping lists of entities
    that only participated in Indianapolis 500 races, reducing code duplication
    across different entity types (constructors, engine manufacturers, etc.).

    Subclasses should set:
    - url: The Wikipedia URL to scrape from
    - record_key: The field name for the entity (e.g., "constructor", "manufacturer")
    - url_key: The field name for the entity URL
      (e.g., "constructor_url", "manufacturer_url")
    """

    section_id = "Indianapolis_500_only"
