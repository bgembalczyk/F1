from typing import Any, Dict, List

from bs4 import BeautifulSoup

from models.records.link import LinkRecord
from scrapers.base.helpers.text import extract_links_from_cell
from scrapers.base.helpers.wiki import build_full_url


class InfoboxHtmlParser:
    """Parser HTML infoboxów z Wikipedii (tytuł, wiersze, linki)."""

    WIKIPEDIA_BASE = "https://en.wikipedia.org"

    def __init__(self, wikipedia_base: str | None = None) -> None:
        self.wikipedia_base = wikipedia_base or self.WIKIPEDIA_BASE

    def parse(self, soup: BeautifulSoup) -> Dict[str, Any]:
        infobox = self.find_infobox(soup)
        if infobox is None:
            return {"title": None, "rows": {}}

        return self._parse_infobox(infobox)

    @staticmethod
    def _has_infobox_class(c) -> bool:
        """Sprawdza czy element zawiera klasę 'infobox'."""
        if not c:
            return False
        if isinstance(c, str):
            classes = c.split()
        else:
            # BeautifulSoup zwykle daje listę
            try:
                classes = list(c)
            except TypeError:
                return False
        return "infobox" in classes

    @staticmethod
    def find_infobox(soup: BeautifulSoup):
        """
        Znajduje <table> z klasą zawierającą 'infobox' w ramach przekazanego `soup`.

        Obsługuje zarówno:
        - class="infobox vcard"
        - class=["infobox", "vcard"]
        """
        return soup.find("table", class_=InfoboxHtmlParser._has_infobox_class)

    def _parse_infobox(self, table) -> Dict[str, Any]:
        data: Dict[str, Any] = {"title": None, "rows": {}}

        # Tytuł (często <caption>)
        caption = table.find("caption")
        if caption:
            data["title"] = caption.get_text(" ", strip=True)

        # Faktyczne wiersze infoboksa. W artykułach Wikipedii <tr> znajdują się
        # zwykle wewnątrz <tbody>, dlatego szukamy w całej tabeli, ale
        # odfiltrowujemy wiersze zagnieżdżonych tabel.
        for tr in table.find_all("tr"):
            # pomiń wiersze należące do zagnieżdżonych tabel (np. miniaturek)
            if tr.find_parent("table") is not table:
                continue

            header = tr.find("th", recursive=False)
            value = tr.find("td", recursive=False)

            # ignorujemy wiersze bez pary th/td
            if not header or not value:
                continue

            key = header.get_text(" ", strip=True)
            text = value.get_text(" ", strip=True)
            links = self.extract_links(value)

            data["rows"][key] = {"text": text, "links": links}

        return data

    def extract_links(self, td) -> List[LinkRecord]:
        """
        Wyciąga wszystkie linki z komórki, pomijając linki do przypisów.
        """
        return extract_links_from_cell(
            td,
            full_url=lambda href: build_full_url(self.wikipedia_base, href),
            allow_local_anchors=False,
        )
