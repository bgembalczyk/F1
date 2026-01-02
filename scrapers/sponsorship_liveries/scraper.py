from pathlib import Path
from typing import Any
from typing import Dict, List

from bs4 import BeautifulSoup

from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.helpers.runner import run_and_export
from scrapers.base.options import ScraperOptions
from scrapers.base.run_config import RunConfig
from scrapers.base.scraper import F1Scraper
from scrapers.sponsorship_liveries.parsers.sponsorship_record_splitter import (
    SponsorshipRecordSplitter,
)
from scrapers.sponsorship_liveries.parsers.sponsorship_section_parser import (
    SponsorshipSectionParser,
)


class F1SponsorshipLiveriesScraper(F1Scraper):
    """
    Scraper tabel sponsorskich malowań F1:
    https://en.wikipedia.org/wiki/Formula_One_sponsorship_liveries

    Każda sekcja to jeden zespół, a w sekcji znajduje się tabela z kolumnami
    (opcjonalnymi) dotyczącymi sezonu i zmian malowania.
    """

    url = "https://en.wikipedia.org/wiki/Formula_One_sponsorship_liveries"

    def __init__(self, *, options: ScraperOptions | None = None) -> None:
        options = init_scraper_options(options, include_urls=True)
        options.with_fetcher()
        super().__init__(options=options)
        self._splitter = SponsorshipRecordSplitter()
        self._section_parser = SponsorshipSectionParser(
            include_urls=self.include_urls,
            splitter=self._splitter,
        )

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        return self._section_parser.parse_sections(soup)


if __name__ == "__main__":
    run_and_export(
        F1SponsorshipLiveriesScraper,
        "sponsorship_liveries/f1_sponsorship_liveries.json",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
        ),
    )
