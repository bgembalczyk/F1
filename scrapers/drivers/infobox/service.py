from __future__ import annotations

from typing import TYPE_CHECKING

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.infobox.service import BaseInfoboxExtractionService
from scrapers.base.infobox.service import FirstInfoboxTableExtractor
from scrapers.drivers.infobox.scraper import DriverInfoboxParser

if TYPE_CHECKING:
    from collections.abc import Iterable

    from scrapers.base.options import ScraperOptions
    from scrapers.base.parsers.soup import SoupParser


class DriverInfoboxExtractionService(BaseInfoboxExtractionService[Tag]):
    def __init__(self, *, options: ScraperOptions | None = None) -> None:
        super().__init__(options=options)
        self._infobox_locator = FirstInfoboxTableExtractor()

    def find_infoboxes(self, soup: BeautifulSoup) -> Iterable[Tag]:
        return self._infobox_locator.find_infoboxes(soup)

    def build_parser(self, *, url: str) -> SoupParser:
        return DriverInfoboxParser(
            options=self._options,
            run_id=self._options.run_id,
            url=url,
        )
