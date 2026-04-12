from typing import Any

from bs4 import BeautifulSoup

from scrapers.config_table import TableScraperConfig
from scrapers.options import ScraperOptions
from scrapers.parsers.section.standings.f1_table import F1StandingsTableParser
from scrapers.scraper_table import F1TableScraper


class F1StandingsScraper(F1TableScraper):
    """Pełny scraper standings z pipeline fetch/parse."""

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        config: TableScraperConfig | None = None,
        position_key: str = "pos",
    ) -> None:
        super().__init__(options=options, config=config)
        self._table_parser = F1StandingsTableParser(position_key=position_key)

    def _parse_soup(self, soup: BeautifulSoup) -> list[Any]:
        rows = super()._parse_soup(soup)
        return self._table_parser.normalize_rows(rows)
