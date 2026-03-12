from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup

from scrapers.base.ABC import F1Scraper
from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.helpers.runner import run_and_export
from scrapers.base.options import ScraperOptions
from scrapers.base.run_config import RunConfig
from scrapers.sponsorship_liveries.parsers.record_splitter import (
    SponsorshipRecordSplitter,
)
from scrapers.sponsorship_liveries.parsers.section_parser import (
    SponsorshipSectionParser,
)

if TYPE_CHECKING:
    from scrapers.sponsorship_liveries.helpers.paren_classifier import ParenClassifier


class F1SponsorshipLiveriesScraper(F1Scraper):
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
        policy = self.get_http_policy(options)
        options.with_fetcher(policy=policy)
        super().__init__(options=options)
        self._splitter = SponsorshipRecordSplitter()
        self._section_parser = SponsorshipSectionParser(
            url=self.url,
            include_urls=self.include_urls,
            normalize_empty_values=self.normalize_empty_values,
            splitter=self._splitter,
            classifier=classifier,
        )

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        return self._section_parser.parse_sections(soup)


if __name__ == "__main__":
    from scrapers.sponsorship_liveries.helpers.paren_classifier import ParenClassifier
    from infrastructure.gemini.client import GeminiClient

    try:
        _gemini_client = GeminiClient.from_key_file()
        _classifier: Optional[ParenClassifier] = ParenClassifier(_gemini_client)
        print("[scraper] Gemini ParenClassifier załadowany – adnotacje w nawiasach będą klasyfikowane.")
    except FileNotFoundError as _e:
        _classifier = None
        print("[scraper] Brak klucza Gemini API ({_e}), klasyfikacja Gemini wyłączona.")

    run_and_export(
        F1SponsorshipLiveriesScraper,
        "sponsorship_liveries/f1_sponsorship_liveries.json",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
            scraper_kwargs={"classifier": _classifier},
        ),
    )
