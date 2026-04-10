from __future__ import annotations

from typing import TYPE_CHECKING

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.infobox.extraction.extractor.table.first import FirstInfoboxTableExtractor
from scrapers.infobox.extraction.service.contracts import BaseInfoboxExtractionService
from scrapers.infobox.scraper_drivers import DriverInfoboxParser
from scrapers.options import ScraperOptions
from scrapers.parsers.soup import SoupParser

if TYPE_CHECKING:
    from collections.abc import Iterable



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


__all__ = ["DriverInfoboxExtractionService"]
