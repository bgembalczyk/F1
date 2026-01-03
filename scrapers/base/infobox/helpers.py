from typing import Any
from typing import Dict

from bs4 import BeautifulSoup

from scrapers.base.debug_dumps import write_infobox_dump
from scrapers.base.infobox.scraper import WikipediaInfoboxScraper


def parse_infobox_from_soup(
    infobox_scraper: WikipediaInfoboxScraper,
    soup: BeautifulSoup,
) -> Dict[str, Any]:
    try:
        raw = infobox_scraper.parser.parse(soup)
        mapped = infobox_scraper.mapper.map(raw)
        return infobox_scraper.apply_record_factory(mapped)
    except Exception:
        debug_dir = getattr(infobox_scraper, "debug_dir", None)
        if debug_dir is not None:
            table = infobox_scraper.parser.find_infobox(soup)
            if table is not None:
                url = getattr(infobox_scraper, "url", None)
                run_id = getattr(infobox_scraper, "run_id", None)
                dump_path = write_infobox_dump(
                    debug_dir,
                    html=str(table),
                    url=url,
                    run_id=run_id,
                )
                logger = getattr(infobox_scraper, "logger", None)
                if logger is not None:
                    logger.warning(
                        "Saved infobox HTML dump: %s (url=%s)",
                        dump_path,
                        url,
                    )
        raise
