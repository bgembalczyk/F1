from __future__ import annotations

from typing import TYPE_CHECKING

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.infobox.extraction.extractor.table.all import AllInfoboxTablesExtractor
from scrapers.infobox.extraction.service.base_infobox_orchestrator import (
    BaseInfoboxOrchestrator,
)
from scrapers.options import ScraperOptions
from scrapers.parsers.infobox.wiki_html import WikiInfoboxHtmlParser
from scrapers.parsers.soup import SoupParser

if TYPE_CHECKING:
    from collections.abc import Iterable


class ConstructorInfoboxOrchestrator(BaseInfoboxOrchestrator[Tag]):
    def __init__(self, *, options: ScraperOptions | None = None) -> None:
        super().__init__(options=options)
        self._infobox_locator = AllInfoboxTablesExtractor()

    def find_infoboxes(self, soup: BeautifulSoup) -> Iterable[Tag]:
        return self._infobox_locator.find_infoboxes(soup)

    def build_parser(self, *, url: str) -> SoupParser:
        _ = url
        return WikiInfoboxHtmlParser()
