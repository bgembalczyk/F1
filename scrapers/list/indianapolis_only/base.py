from scrapers.list.indianapolis_only.mixin import IndianapolisOnlyMixin
from scrapers.list.base import ListScraper


class IndianapolisOnlyListScraper(IndianapolisOnlyMixin, ListScraper):
    """Backward-compatible Indianapolis-only list scraper base class."""
