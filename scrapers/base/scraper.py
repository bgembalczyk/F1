from __future__ import annotations

from abc import ABC
import logging
from typing import Any, Dict, List, Optional, Sequence

from bs4 import BeautifulSoup
from urllib.parse import urljoin

from scrapers.base.errors import (
    ScraperError,
    ScraperNetworkError,
    ScraperParseError,
)
from scrapers.base.exporters import DataExporter
from scrapers.base.results import ScrapeResult
from scrapers.base.html_fetcher import HtmlFetcher
from scrapers.base.parsers import SoupParser


logger = logging.getLogger(__name__)


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

        self._data: List[Dict[str, Any]] = []

    # ---------- API wysokiego poziomu ----------

    def fetch(self) -> List[Dict[str, Any]]:
        """Pobierz dane z sieci i sparsuj je do listy słowników."""
        try:
            html = self._download()
        except ScraperError as exc:
            if self._handle_scraper_error(exc):
                self._data = []
                return self._data
            raise
        except Exception as exc:
            raise self._wrap_network_error(exc) from exc

        try:
            soup = BeautifulSoup(html, "html.parser")
            parser = self.parser or self
            self._data = parser.parse(soup)
        except ScraperError as exc:
            if self._handle_scraper_error(exc):
                self._data = []
                return self._data
            raise
        except Exception as exc:
            parse_error = self._wrap_parse_error(exc)
            if self._handle_scraper_error(parse_error):
                self._data = []
                return self._data
            raise parse_error from exc

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
        return self.fetcher.get_text(self.url)

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parsowanie BS4 -> lista rekordów."""
        raise NotImplementedError

    def parse(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        return self._parse_soup(soup)

    # ---------- Pomocnicze ----------

    def _full_url(self, href: str | None) -> Optional[str]:
        if not href:
            return None
        # Linki wewnętrzne z Wikipedii typu "/wiki/..."
        return urljoin(self.url, href)

    def _wrap_network_error(self, exc: Exception) -> ScraperNetworkError:
        return ScraperNetworkError(
            "Błąd sieci podczas pobierania danych.",
            url=getattr(self, "url", None),
            cause=exc,
        )

    def _wrap_parse_error(self, exc: Exception) -> ScraperParseError:
        return ScraperParseError(
            "Błąd parsowania danych.",
            url=getattr(self, "url", None),
            cause=exc,
        )

    def _handle_scraper_error(self, error: ScraperError) -> bool:
        if error.critical:
            return False
        logger.warning(
            "Pomijam dane ze względu na błąd: %s",
            error,
        )
        return True
