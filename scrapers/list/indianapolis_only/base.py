from scrapers.list.base import ListScraper
from scrapers.list.indianapolis_only.mixin import IndianapolisOnlyMixin


class IndianapolisOnlyListScraper(IndianapolisOnlyMixin, ListScraper):
    """Backward-compatible Indianapolis-only list scraper base class."""
