from __future__ import annotations

from typing import Any, Dict, List

from bs4 import BeautifulSoup

from scrapers.base.helpers.wiki import is_reference_link


class InfoboxHtmlParser:
    """Parser HTML infoboxów z Wikipedii (tytuł, wiersze, linki)."""

    WIKIPEDIA_BASE = "https://en.wikipedia.org"

    def __init__(self, wikipedia_base: str | None = None) -> None:
        self.wikipedia_base = wikipedia_base or self.WIKIPEDIA_BASE

    def parse(self, soup: BeautifulSoup) -> Dict[str, Any]:
        infobox = self._find_infobox(soup)
        if infobox is None:
            return {"title": None, "rows": {}}

        return self._parse_infobox(infobox)

    def parse_from_soup(self, soup: BeautifulSoup) -> Dict[str, Any]:
        return self.parse(soup)

    def _find_infobox(self, soup: BeautifulSoup):
        """
        Znajduje <table> z klasą zawierającą 'infobox' w ramach przekazanego `soup`.

        Obsługuje zarówno:
        - class="infobox vcard"
        - class=["infobox", "vcard"]
        """

        def _has_infobox_class(c) -> bool:
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

        return soup.find("table", class_=_has_infobox_class)

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
            links = self._extract_links(value)

            data["rows"][key] = {"text": text, "links": links}

        return data

    def _extract_links(self, td) -> List[dict]:
        """
        Wyciąga wszystkie linki z komórki, pomijając linki do przypisów.
        """
        links = []
        for a in td.find_all("a", href=True):
            href = a["href"]

            # ignorujemy przypisy i lokalne kotwice
            if is_reference_link(a):
                continue

            # zamiana na absolutny URL
            if href.startswith("/"):
                href = f"{self.wikipedia_base}{href}"

            links.append({"text": a.get_text(" ", strip=True), "url": href})

        return links
