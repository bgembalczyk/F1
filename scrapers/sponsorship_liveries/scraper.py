from typing import TYPE_CHECKING
from typing import Any
from typing import Optional

from bs4 import BeautifulSoup

from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.options import ScraperOptions
from scrapers.sponsorship_liveries.parsers.splitters.record.facade import (
    SponsorshipRecordSplitter,
)
from scrapers.sponsorship_liveries.parsers.team_liveries import (
    TeamLiveriesSectionParser,
)
from scrapers.wiki.scraper import WikiScraper

if TYPE_CHECKING:
    from scrapers.sponsorship_liveries.helpers.paren_classifier import ParenClassifier


class F1SponsorshipLiveriesScraper(WikiScraper):
    """
    Scraper tabel sponsorskich malowań F1:
    https://en.wikipedia.org/wiki/Formula_One_sponsorship_liveries

    Każda sekcja to jeden zespół, a w sekcji znajduje się tabela z kolumnami
    (opcjonalnymi) dotyczącymi sezonu i zmian malowania.

    Parameters
    ----------
    classifier:
        Opcjonalny klasyfikator Gemini do semantycznej analizy nawiasowych
        adnotacji w kolumnie roku.  Jeśli nie zostanie podany, klasyfikacja
        nie jest wykonywana.
    """

    url = "https://en.wikipedia.org/wiki/Formula_One_sponsorship_liveries"

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        classifier: Optional["ParenClassifier"] = None,
    ) -> None:
        options = init_scraper_options(options, include_urls=True)
        super().__init__(options=options)
        self._splitter = SponsorshipRecordSplitter()
        self._section_parser = TeamLiveriesSectionParser(
            url=self.url,
            include_urls=self.include_urls,
            normalize_empty_values=self.normalize_empty_values,
            splitter=self._splitter,
            classifier=classifier,
        )

    def _parse_soup(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        return self._section_parser.parse_sections(soup)
