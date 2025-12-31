from __future__ import annotations

from typing import Any, Dict, List

from bs4 import BeautifulSoup

from scrapers.base.options import ScraperOptions
from scrapers.base.table.scraper import F1TableScraper
from scrapers.base.table.columns.types.position import PositionColumn
from scrapers.base.table.config import ScraperConfig


class F1StandingsScraper(F1TableScraper):
    def __init__(
        self,
        *,
        options: ScraperOptions,
        config: ScraperConfig,
        position_key: str = "pos",
    ) -> None:
        self.position_key = position_key
        super().__init__(options=options, config=config)

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        rows = super()._parse_soup(soup)
        previous_position = None
        for row in rows:
            pos = row.get(self.position_key)
            if pos is PositionColumn.TIED:
                row[self.position_key] = previous_position
            elif pos is not None:
                previous_position = pos
        return rows
