from __future__ import annotations

from bs4 import BeautifulSoup
from typing import Any, Dict, List, Optional

import requests

from http_client.clients import UrllibHttpClient
from http_client.interfaces import HttpClientProtocol
from http_client.policies import ResponseCache, RetryPolicy, RateLimiter
from scrapers.base.helpers.utils import is_reference_link


class WikipediaInfoboxScraper:
    """
    Scraper infoboksów z artykułów Wikipedii.

    Użycie:
        scraper = WikipediaInfoboxScraper()
        data = scraper.scrape("https://en.wikipedia.org/wiki/Lewis_Hamilton")
    """

    WIKIPEDIA_BASE = "https://en.wikipedia.org"

    def __init__(
        self,
        *,
        user_agent: str | None = None,
        timeout: int = 10,
        session: Optional[requests.Session] = None,
        headers: Optional[Dict[str, str]] = None,
        http_client: Optional[HttpClientProtocol] = None,
        cache: ResponseCache | None = None,
        retry_policy: RetryPolicy | None = None,
        rate_limiter: RateLimiter | None = None,
    ):
        merged_headers: Dict[str, str] = {}
        if user_agent:
            merged_headers["User-Agent"] = user_agent
        if headers:
            merged_headers.update(headers)

        if http_client is None:
            http_client = UrllibHttpClient(
                session=session,
                headers=merged_headers or None,
                timeout=timeout,
                retry_policy=retry_policy,
                rate_limiter=rate_limiter,
                cache=cache,
            )
        self.http_client = http_client
        self.session = getattr(self.http_client, "session", None)
        self.headers = getattr(self.session, "headers", {})
        self.timeout = timeout

    # ------------------------------
    # Public API
    # ------------------------------

    def scrape(self, url: str) -> Dict[str, Any]:
        """Pobiera i parsuje infobox z dowolnego artykułu Wikipedii."""
        html = self._fetch(url)
        soup = BeautifulSoup(html, "html.parser")
        return self.parse_from_soup(soup)

    def parse_from_soup(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Parsuje infobox z już utworzonego obiektu ``BeautifulSoup``."""
        infobox = self._find_infobox(soup)
        if infobox is None:
            return {"title": None, "rows": {}}

        return self._parse_infobox(infobox)

    # ------------------------------
    # Internal helpers
    # ------------------------------

    def _fetch(self, url: str) -> str:
        return self.http_client.get_text(url, timeout=self.timeout)

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
                href = f"{self.WIKIPEDIA_BASE}{href}"

            links.append({"text": a.get_text(" ", strip=True), "url": href})

        return links
