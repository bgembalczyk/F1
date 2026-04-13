from scrapers.list.base import ListScraper
from scrapers.list.indianapolis_only.config import IndianapolisOnlyListConfig


class IndianapolisOnlyListScraper(ListScraper):
    """Backward-compatible Indianapolis-only list scraper base class."""

    section_id = "Indianapolis_500_only"
    domain_name: str | None = None
    record_type: str | None = None
    CONFIG: IndianapolisOnlyListConfig | None = None
