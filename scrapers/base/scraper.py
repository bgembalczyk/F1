from __future__ import annotations

import warnings
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from bs4 import BeautifulSoup
from urllib.parse import urljoin

from scrapers.base.exporters import DataExporter
from scrapers.base.html_fetcher import HtmlFetcher
from scrapers.base.options import ScraperOptions
from scrapers.base.results import ScrapeResult


class F1Scraper(ABC):
    """
    Bazowa klasa dla wszystkich scraperów F1.

    Odpowiada za:
    - orkiestrację download → parse → build result
    - trzymanie danych w pamięci
    - delegowanie eksportu
    """

    url: str  # pełny URL strony Wikipedii

    def __init__(self, *, options: ScraperOptions) -> None:
        self.include_urls = options.include_urls

        # Preferuj gotowy fetcher w options.
        # Jeśli nie ma — budujemy HtmlFetcher z pól opcji (legacy).
        if options.fetcher is None:
            legacy_used = any(
                value is not None
                for value in (
                    options.session,
                    options.headers,
                    options.http_client,
                    options.timeout,
                    options.retries,
                    options.cache,
                )
            )
            if legacy_used:
                warnings.warn(
                    "Konfigurację HTTP przekazuj przez skonfigurowany HttpClient "
                    "(ScraperOptions.http_client) albo gotowy HtmlFetcher "
                    "(ScraperOptions.fetcher). Parametry session/headers/timeout/"
                    "retries/cache w ScraperOptions traktuj jako legacy.",
                    DeprecationWarning,
                    stacklevel=2,
                )

            self.fetcher = HtmlFetcher(
                session=options.session,
                headers=options.headers,
                http_client=options.http_client,
                timeout=options.timeout,
                retries=options.retries,
                cache=options.cache,
            )
        else:
            self.fetcher = options.fetcher

        # Parser może być zewnętrzny (np. mixin/adapter).
        self.parser = options.parser
        self.exporter = options.exporter or DataExporter()

        self._data: List[Dict[str, Any]] = []

    # ---------- API wysokiego poziomu ----------

    def fetch(self) -> List[Dict[str, Any]]:
        """Pobierz HTML i sparsuj do listy rekordów."""
        html = self._download()
        soup = BeautifulSoup(html, "html.parser")
        parser = self.parser or self
        self._data = parser.parse(soup)
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
        self,
        path: str | Path,
        *,
        indent: int = 2,
        include_metadata: bool = False,
    ) -> None:
        result = self.build_result()
        self.exporter.to_json(
            result,
            path,
            indent=indent,
            include_metadata=include_metadata,
        )

    def to_csv(
        self,
        path: str | Path,
        *,
        fieldnames: Optional[Sequence[str]] = None,
        fieldnames_strategy: str = "union",
    ) -> None:
        result = self.build_result()
        self.exporter.to_csv(
            result,
            path,
            fieldnames=fieldnames,
            fieldnames_strategy=fieldnames_strategy,
        )

    def to_dataframe(self):
        result = self.build_result()
        return self.exporter.to_dataframe(result)

    # ---------- Metody wewnętrzne ----------

    def _download(self) -> str:
        # Fetcher jest jedyną “bramką” do HTTP.
        return self.fetcher.get_text(self.url)

    @abstractmethod
    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parsowanie BS4 -> lista rekordów."""
        raise NotImplementedError

    def parse(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        # publiczna metoda parse deleguje do _parse_soup
        return self._parse_soup(soup)

    # ---------- Pomocnicze ----------

    def _full_url(self, href: str | None) -> Optional[str]:
        if not href:
            return None
        return urljoin(self.url, href)
