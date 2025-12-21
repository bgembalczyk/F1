from __future__ import annotations

from abc import ABC
from typing import Optional, Sequence

from pathlib import Path

from bs4 import BeautifulSoup
from urllib.parse import urljoin

import requests

from http_client.caching import WikipediaCachePolicy, FileCache
from http_client.clients import UrllibHttpClient
from http_client.interfaces import HttpClientProtocol
from http_client.policies import ResponseCache
from scrapers.base.exporters import DataExporter
from scrapers.base.results import ScrapeResult
from scrapers.base.html_fetcher import HtmlFetcher
from scrapers.base.parsers import SoupParser
from scrapers.base.types import ExportableRecord


# ======================================================================
# BAZA
# ======================================================================


class F1Scraper(ABC):
    """
    Bazowa klasa dla wszystkich scrapperów F1.

    Odpowiada za:
    - orkiestrację fetch → parse → build result
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
        exporter: Optional[DataExporter] = None,
        fetcher: HtmlFetcher | None = None,
        parser: SoupParser | None = None,
    ) -> None:
        self.include_urls = include_urls
        self.fetcher = fetcher or HtmlFetcher()
        self.parser = parser
        self.exporter = exporter or DataExporter()

        self._data: list[ExportableRecord] = []

    # ---------- API wysokiego poziomu ----------

    def fetch(self) -> list[ExportableRecord]:
        """Pobierz dane z sieci i sparsuj je do listy słowników."""
        html = self._download()
        soup = BeautifulSoup(html, "html.parser")
        parser = self.parser or self
        self._data = parser.parse(soup)
        return self._data

    def get_data(self) -> list[ExportableRecord]:
        """Zwróć dane – jeśli jeszcze nie ma, uruchom fetch()."""
        if not self._data:
            self.fetch()
        return self._data

    def build_result(
        self, data: Optional[list[ExportableRecord]] = None
    ) -> ScrapeResult:
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
        return self.fetcher.get_text(self.url)

    def _parse_soup(self, soup: BeautifulSoup) -> list[ExportableRecord]:
        """Parsowanie BS4 -> lista rekordów."""
        raise NotImplementedError

    def parse(self, soup: BeautifulSoup) -> list[ExportableRecord]:
        return self._parse_soup(soup)

    # ---------- Pomocnicze ----------

    def _full_url(self, href: str | None) -> Optional[str]:
        if not href:
            return None
        # Linki wewnętrzne z Wikipedii typu "/wiki/..."
        return urljoin(self.url, href)
