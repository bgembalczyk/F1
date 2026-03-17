from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from scrapers.base.infobox.html_parser import InfoboxHtmlParser

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


class ConstructorInfoboxExtractionService:
    def __init__(self) -> None:
        self._parser = InfoboxHtmlParser()

    def extract(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        return [
            self._parser.parse_element(table)
            for table in soup.find_all("table", class_="infobox")
        ]
