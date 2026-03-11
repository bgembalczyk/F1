from typing import Any
from typing import Dict
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup

from scrapers.base.extractors.infobox import InfoboxExtractor

# Unikamy cyklicznego importu – import tylko dla typowania
if TYPE_CHECKING:
    from scrapers.base.infobox.scraper import WikipediaInfoboxScraper


def parse_infobox_from_soup(
        infobox_scraper: "WikipediaInfoboxScraper",
        soup: BeautifulSoup,
) -> Dict[str, Any]:
    extractor = InfoboxExtractor(
        parser=infobox_scraper.parser,
        mapper=infobox_scraper.mapper,
        logger=getattr(infobox_scraper, "logger", None),
        debug_dir=getattr(infobox_scraper, "debug_dir", None),
        run_id=getattr(infobox_scraper, "run_id", None),
        url=getattr(infobox_scraper, "url", None),
    )
    return extractor.extract(soup)
