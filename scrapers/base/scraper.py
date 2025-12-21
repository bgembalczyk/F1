from __future__ import annotations

import logging
import warnings
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Sequence
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from scrapers.base.exporters import DataExporter
from scrapers.base.html_fetcher import HtmlFetcher
from scrapers.base.options import ScraperOptions
from scrapers.base.records import ExportRecord, NormalizedRecord, RawRecord
from scrapers.base.results import ScrapeResult

# PR wnosił ustandaryzowane wyjątki – używamy ich jeśli istnieją w projekcie.
from scrapers.base.errors import ScraperError, ScraperNetworkError, ScraperParseError



logger = logging.getLogger(__name__)


class F1Scraper(ABC):
    """
    Bazowa klasa dla wszystkich scraperów F1.

    Odpowiada za:
    - orkiestrację download → parse → normalize → export-records
    - trzymanie danych w pamięci
    - delegowanie eksportu
    - wspólną obsługę błędów (network/parse + soft-skip)
    """

    #: Pełny URL strony Wikipedii (ustawiany w klasach potomnych)
    url: str

    def __init__(self, *, options: ScraperOptions) -> None:
        self.include_urls = options.include_urls

        # Preferuj gotowy fetcher w options.
        # HtmlFetcher po merge jest config-driven (default_http_config),
        # więc jeśli go nie ma — tworzymy go "domyślnie".
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
                    "retries/cache w ScraperOptions traktuj jako legacy i nie są "
                    "już używane do budowy HtmlFetcher.",
                    DeprecationWarning,
                    stacklevel=2,
                )

            self.fetcher = HtmlFetcher()
        else:
            self.fetcher = options.fetcher

        # Parser może być zewnętrzny (np. mixin/adapter).
        self.parser = options.parser
        self.exporter = options.exporter or DataExporter()

        self._data: Optional[List[ExportRecord]] = None

    # ---------- API wysokiego poziomu ----------

    def fetch(self) -> List[ExportRecord]:
        """
        Pobierz HTML i sparsuj do listy rekordów eksportowych.

        Pipeline:
        - download
        - parse -> RawRecord[]
        - normalize_records -> NormalizedRecord[]
        - to_export_records -> ExportRecord[]

        Error handling:
        - ScraperError z critical=True -> propagujemy
        - pozostałe -> warning + soft-skip (puste dane)
        """
        if not getattr(self, "url", None):
            raise ValueError("Scraper.url musi być ustawiony przed fetch().")

        try:
            html = self._download()
        except ScraperError as exc:  # type: ignore[misc]
            if self._handle_scraper_error(exc):
                self._data = []
                return self._data
            raise
        except Exception as exc:
            wrapped = self._wrap_network_error(exc)
            if self._handle_scraper_error(wrapped):
                self._data = []
                return self._data
            raise wrapped from exc

        try:
            soup = BeautifulSoup(html, "html.parser")

            # Poprawka: zawsze wołamy publiczne parse(), a nie zakładamy .parse na parserze
            if self.parser is None:
                raw_records = self.parse(soup)
            else:
                raw_records = self.parser.parse(soup)  # type: ignore[call-arg, attr-defined]

            normalized_records = self.normalize_records(raw_records)
            self._data = self.to_export_records(normalized_records)
        except ScraperError as exc:  # type: ignore[misc]
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

    def get_data(self) -> List[ExportRecord]:
        """Zwróć dane – jeśli jeszcze nie ma, uruchom fetch()."""
        if self._data is None:
            return self.fetch()
        return self._data

    def build_result(self, data: Optional[List[ExportRecord]] = None) -> ScrapeResult:
        """Utwórz ScrapeResult z metadanymi."""
        return ScrapeResult(
            data=data if data is not None else self.get_data(),
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
    def _parse_soup(self, soup: BeautifulSoup) -> List[RawRecord]:
        """Parsowanie BS4 -> lista rekordów surowych."""
        raise NotImplementedError

    def parse(self, soup: BeautifulSoup) -> List[RawRecord]:
        # publiczna metoda parse deleguje do _parse_soup
        return self._parse_soup(soup)

    # ---------- Hooki: normalize/export ----------

    def normalize_records(self, records: List[RawRecord]) -> List[NormalizedRecord]:
        return records

    def to_export_records(self, records: List[NormalizedRecord]) -> List[ExportRecord]:
        return records

    # ---------- Pomocnicze ----------

    def _full_url(self, href: str | None) -> Optional[str]:
        if not href:
            return None
        return urljoin(self.url, href)

    # ---------- Error handling ----------

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

    def _handle_scraper_error(self, error: Exception) -> bool:
        """
        Domyślne zachowanie:
        - jeśli błąd ma atrybut `critical=True` -> nie połykamy
        - inaczej logujemy warning i soft-skip (zwracamy puste dane)
        """
        critical = bool(getattr(error, "critical", False))
        if critical:
            return False

        logger.warning("Pomijam dane ze względu na błąd: %s", error)
        return True
