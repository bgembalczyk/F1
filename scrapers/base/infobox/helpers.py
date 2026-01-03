from typing import Any
from typing import Dict

from bs4 import BeautifulSoup

from scrapers.base.infobox.scraper import WikipediaInfoboxScraper


def parse_infobox_from_soup(
    infobox_scraper: WikipediaInfoboxScraper,
    soup: BeautifulSoup,
) -> Dict[str, Any]:
    raw = infobox_scraper.parser.parse(soup)
    mapped = infobox_scraper.mapper.map(raw)
    return infobox_scraper.apply_record_factory(mapped)
