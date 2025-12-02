from __future__ import annotations

import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List


class WikipediaInfoboxScraper:
    """
    Scraper infoboksów z artykułów Wikipedii.

    Użycie:
        scraper = WikipediaInfoboxScraper()
        data = scraper.scrape("https://en.wikipedia.org/wiki/Lewis_Hamilton")
    """

    WIKIPEDIA_BASE = "https://en.wikipedia.org"

    def __init__(self, *, user_agent: str | None = None, timeout: int = 10):
        self.timeout = timeout
        self.headers = {
            "User-Agent": user_agent
            or "Mozilla/5.0 (compatible; F1AI-InfoboxScraper/1.0)"
        }

    # ------------------------------
    # Public API
    # ------------------------------

    def scrape(self, url: str) -> Dict[str, Any]:
        """Pobiera i parsuje infobox z dowolnego artykułu Wikipedii."""
        html = self._fetch(url)
        soup = BeautifulSoup(html, "html.parser")

        infobox = self._find_infobox(soup)
        if infobox is None:
            return {"title": None, "rows": {}}

        return self._parse_infobox(infobox)

    # ------------------------------
    # Internal helpers
    # ------------------------------

    def _fetch(self, url: str) -> str:
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        return response.text

    def _find_infobox(self, soup: BeautifulSoup):
        """
        Znajduje <table class="infobox ...">.
        Często infoboksy mają wiele klas: infobox biography, infobox vcard itd.
        """
        return soup.find("table", class_=lambda c: c and "infobox" in c.split())

    def _parse_infobox(self, table) -> Dict[str, Any]:
        data: Dict[str, Any] = {"title": None, "rows": {}}

        # Tytuł (często <caption>)
        caption = table.find("caption")
        if caption:
            data["title"] = caption.get_text(" ", strip=True)

        # Faktyczne wiersze infoboksa
        for tr in table.find_all("tr", recursive=False):
            header = tr.find("th")
            value = tr.find("td")

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
            if href.startswith("#") or "cite_note" in href:
                continue

            # zamiana na absolutny URL
            if href.startswith("/"):
                href = f"{self.WIKIPEDIA_BASE}{href}"

            links.append({
                "text": a.get_text(" ", strip=True),
                "url": href
            })

        return links
