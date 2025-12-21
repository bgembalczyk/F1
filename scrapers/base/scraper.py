from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from bs4 import BeautifulSoup
from urllib.parse import urljoin

import requests

from f1_http.interfaces import HttpClientProtocol
from http_client import HttpClient
from scrapers.base.exporters import DataExporter, ScrapeResult


# ======================================================================
# BAZA
# ======================================================================


class F1Scraper(ABC):
    """
    Bazowa klasa dla wszystkich scrapperów F1.

    Odpowiada za:
    - pobranie HTML (requests)
    - trzymanie danych w pamięci
    - delegowanie eksportu
    - szablon metody fetch()
    """

    #: Pełny URL strony Wikipedii
    url: str

    def __init__(
        self,
        *,
        include_urls: bool = True,
        session: Optional[requests.Session] = None,
        headers: Optional[Dict[str, str]] = None,
        http_client: Optional[HttpClientProtocol] = None,
        exporter: Optional[DataExporter] = None,
        timeout: int = 10,
        retries: int = 0,
    ) -> None:
        self.include_urls = include_urls
        self.http_client = http_client or HttpClient(
            session=session, headers=headers, timeout=timeout, retries=retries
        )
        self.session = getattr(self.http_client, "session", None)
        self.exporter = exporter or DataExporter()

        self._data: List[Dict[str, Any]] = []

    # ---------- API wysokiego poziomu ----------

    def fetch(self) -> List[Dict[str, Any]]:
        """Pobierz dane z sieci i sparsuj je do listy słowników."""
        html = self._download()
        soup = BeautifulSoup(html, "html.parser")
        self._data = self._parse_soup(soup)
        return self._data

    def get_data(self) -> List[Dict[str, Any]]:
        """Zwróć dane – jeśli jeszcze nie ma, uruchom fetch()."""
        if not self._data:
            self.fetch()
        return self._data

    def build_result(self, data: Optional[List[Dict[str, Any]]] = None) -> ScrapeResult:
        """Utwórz ScrapeResult z metadanymi."""
        return ScrapeResult(
            data=data or self.get_data(),
            source_url=getattr(self, "url", None),
        )

    # ---------- Eksport (delegowany) ----------

    def to_json(
        self, path: str | Path, *, indent: int = 2, include_metadata: bool = False
    ) -> None:
        result = self.build_result()
        self.exporter.to_json(
            result, path, indent=indent, include_metadata=include_metadata
        )

    def to_csv(
        self,
        path: str | Path,
        *,
        fieldnames: Optional[Sequence[str]] = None,
    ) -> None:
        result = self.build_result()
        self.exporter.to_csv(result, path, fieldnames=fieldnames)

    def to_dataframe(self):
        result = self.build_result()
        return self.exporter.to_dataframe(result)

    # ---------- Metody wewnętrzne ----------

    def _download(self) -> str:
        return self.http_client.get_text(self.url)

    @abstractmethod
    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parsowanie BS4 -> lista rekordów."""
        raise NotImplementedError

    # ---------- Pomocnicze ----------

    def _full_url(self, href: str | None) -> Optional[str]:
        if not href:
            return None
        # Linki wewnętrzne z Wikipedii typu "/wiki/..."
        return urljoin(self.url, href)
