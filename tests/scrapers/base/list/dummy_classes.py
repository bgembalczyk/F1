from scrapers.list.base import F1ListScraper

class DummyListScraper(F1ListScraper):
    url = "https://example.com/wiki/List"
    section_id = "Drivers"
    record_key = "driver"


