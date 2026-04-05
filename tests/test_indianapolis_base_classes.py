"""Indianapolis-only scraper contract tests."""

from scrapers.base.list.indianapolis_only_scraper import IndianapolisOnlyListScraper


def test_indianapolis_section_id_is_set() -> None:
    """Indianapolis base scraper has section id configured."""
    assert IndianapolisOnlyListScraper.section_id == "Indianapolis_500_only"
