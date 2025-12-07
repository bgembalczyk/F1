from pathlib import Path
import sys

import pytest

pytest.importorskip("bs4")
pytest.importorskip("requests")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scrapers.base.infobox.scraper import WikipediaInfoboxScraper
from scrapers.grands_prix.F1_grands_prix_list_scraper import F1GrandsPrixListScraper


@pytest.mark.integration
def test_wikipedia_infobox_scraper_retrieves_infobox():
    scraper = WikipediaInfoboxScraper()

    data = scraper.scrape("https://en.wikipedia.org/wiki/Lewis_Hamilton")

    assert data["title"]
    assert data["rows"]


@pytest.mark.integration
def test_f1_scraper_fetches_grand_prix_list():
    scraper = F1GrandsPrixListScraper(include_urls=False)

    records = scraper.fetch()

    assert records
