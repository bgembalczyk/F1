from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Sequence
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from scrapers.base.export.exporters import DataExporter
from scrapers.base.normalization import RecordNormalizer
from scrapers.base.options import ScraperOptions
from scrapers.base.records import ExportRecord, NormalizedRecord, RawRecord
from scrapers.base.results import ScrapeResult

# PR wnosił ustandaryzowane wyjątki – używamy ich jeśli istnieją w projekcie.
from scrapers.base.error_handler import ErrorHandler
from scrapers.base.errors import ScraperError, ScraperNetworkError, ScraperParseError
from scrapers.base.logging import get_logger


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

        # Preferuj gotowy source_adapter w options.
        # HtmlFetcher jest config-driven, więc jeśli go nie ma — tworzymy go "domyślnie".
        self.source_adapter = options.with_source_adapter()
        self.fetcher = options.fetcher

        # Parser może być zewnętrzny (np. mixin/adapter).
        self.parser = options.parser
        self.exporter = options.exporter or DataExporter()
        self._record_normalizer = RecordNormalizer()
        self.logger = get_logger(self.__class__.__name__)
        self._error_handler = ErrorHandler(logger=self.logger)

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
        except Exception as exc:
            error: Exception
            if isinstance(exc, ScraperError):
                error = exc
            else:
                error = self._wrap_network_error(exc)
            if self._handle_scraper_error(error):
                self._data = []
                return self._data
            if error is exc:
                raise
            raise error from exc

        try:
            soup = BeautifulSoup(html, "html.parser")

            raw_records = self.parse(soup)

            normalized_records = self.normalize_records(raw_records)
            self._data = self.to_export_records(normalized_records)
        except Exception as exc:
            error = (
                exc if isinstance(exc, ScraperError) else self._wrap_parse_error(exc)
            )
            if self._handle_scraper_error(error):
                self._data = []
                return self._data
            if error is exc:
                raise
            raise error from exc

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
        result.to_json(
            path,
            exporter=self.exporter,
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
        result.to_csv(
            path,
            exporter=self.exporter,
            fieldnames=fieldnames,
            fieldnames_strategy=fieldnames_strategy,
        )

    def to_dataframe(self):
        result = self.build_result()
        return result.to_dataframe(exporter=self.exporter)

    # ---------- Metody wewnętrzne ----------

    def _download(self) -> str:
        # Adapter jest jedyną “bramką” do źródła.
        return self.source_adapter.get(self.url)

    @abstractmethod
    def _parse_soup(self, soup: BeautifulSoup) -> List[RawRecord]:
        """Parsowanie BS4 -> lista rekordów surowych."""
        raise NotImplementedError

    def parse(self, soup: BeautifulSoup) -> List[RawRecord]:
        if self.parser is None:
            return self._parse_soup(soup)
        return self.parser.parse(soup)

    # ---------- Hooki: normalize/export ----------

    def normalize_records(self, records: List[RawRecord]) -> List[NormalizedRecord]:
        return self._record_normalizer.normalize(list(records))

    def to_export_records(self, records: List[NormalizedRecord]) -> List[ExportRecord]:
        return records

    # ---------- Pomocnicze ----------

    def _full_url(self, href: str | None) -> Optional[str]:
        if not href:
            return None
        return urljoin(self.url, href)

    # ---------- Error handling ----------

    def _wrap_network_error(self, exc: Exception) -> ScraperNetworkError:
        return self._error_handler.wrap_network(exc, url=getattr(self, "url", None))

    def _wrap_parse_error(self, exc: Exception) -> ScraperParseError:
        return self._error_handler.wrap_parse(exc, url=getattr(self, "url", None))

    def _handle_scraper_error(self, error: Exception) -> bool:
        return self._error_handler.handle(error)
