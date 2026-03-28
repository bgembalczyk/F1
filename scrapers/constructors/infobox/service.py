from __future__ import annotations

from typing import TYPE_CHECKING

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.infobox.html_parser import InfoboxHtmlParser
from scrapers.base.infobox.service import AllInfoboxTablesExtractor
from scrapers.base.infobox.service import BaseInfoboxExtractionService

if TYPE_CHECKING:
    from collections.abc import Iterable

    from scrapers.base.options import ScraperOptions
    from scrapers.base.parsers.soup import SoupParser


class ConstructorInfoboxExtractionService(BaseInfoboxExtractionService[Tag]):
    def __init__(self, *, options: ScraperOptions | None = None) -> None:
        super().__init__(options=options)
        self._infobox_locator = AllInfoboxTablesExtractor()

    def find_infoboxes(self, soup: BeautifulSoup) -> Iterable[Tag]:
        return self._infobox_locator.find_infoboxes(soup)

    def build_parser(self, *, url: str) -> SoupParser:
        _ = url
        return InfoboxHtmlParser()
