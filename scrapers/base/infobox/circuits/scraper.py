from __future__ import annotations

from typing import Any, Dict, Optional

from bs4 import BeautifulSoup, Tag

from scrapers.base.html_fetcher import HtmlFetcher
from scrapers.base.infobox.circuits.services.additional_info import (
    CircuitAdditionalInfoParser,
)
from scrapers.base.infobox.circuits.services.entities import CircuitEntitiesParser
from scrapers.base.infobox.circuits.services.entity_parsing import CircuitEntityParser
from scrapers.base.infobox.circuits.services.geo import CircuitGeoParser
from scrapers.base.infobox.circuits.services.history import CircuitHistoryParser
from scrapers.base.infobox.circuits.services.lap_record import CircuitLapRecordParser
from scrapers.base.infobox.circuits.services.layouts import CircuitLayoutsParser
from scrapers.base.infobox.circuits.services.sections import WikipediaSectionExtractor
from scrapers.base.infobox.circuits.services.specs import CircuitSpecsParser
from scrapers.base.infobox.circuits.services.text_utils import InfoboxTextUtils
from scrapers.base.infobox.scraper import WikipediaInfoboxScraper
from scrapers.base.options import ScraperOptions
from scrapers.base.scraper import F1Scraper
from scrapers.base.types import ExportableRecord
from scrapers.config import default_http_config

from scrapers.base.errors import ScraperError, ScraperParseError


class F1CircuitInfoboxScraper(F1Scraper):
    """Parser infoboksów torów F1 z heurystykami pod typowe pola."""

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
    ) -> None:
        options = options or ScraperOptions()

        # Zapewniamy fetcher (spójnie z resztą repo).
        # HtmlFetcher po merge jest config-driven (default_http_config), więc bezpiecznie
        # tworzymy go bez “legacy” parametrów.
        if options.fetcher is None:
            options.fetcher = HtmlFetcher(config=default_http_config())

        super().__init__(options=options)

        # Dla czytelności (F1Scraper i tak to trzyma)
        self.fetcher = options.fetcher
        self.timeout = options.timeout

        # WikipediaInfoboxScraper w stylu "main": przez fetcher
        self.infobox_scraper = WikipediaInfoboxScraper(
            timeout=options.timeout,
            fetcher=options.fetcher,
        )

        # --- Serwisy ---
        self.section_extractor = WikipediaSectionExtractor()
        self.text_utils = InfoboxTextUtils()
        self.geo_parser = CircuitGeoParser()
        self.history_parser = CircuitHistoryParser()
        self.specs_parser = CircuitSpecsParser()
        self.lap_record_parser = CircuitLapRecordParser()
        self.entity_parser = CircuitEntityParser()
        self.additional_info_parser = CircuitAdditionalInfoParser()

        self.entities_parser = CircuitEntitiesParser(
            text_utils=self.text_utils,
            geo_parser=self.geo_parser,
            history_parser=self.history_parser,
            specs_parser=self.specs_parser,
            lap_record_parser=self.lap_record_parser,
            entity_parser=self.entity_parser,
            additional_info_parser=self.additional_info_parser,
        )

        self.layouts_parser = CircuitLayoutsParser(
            infobox_scraper=self.infobox_scraper,
            text_utils=self.text_utils,
            lap_record_parser=self.lap_record_parser,
            specs_parser=self.specs_parser,
        )

        self.url: str = ""

    # ------------------------------
    # Publiczne API
    # ------------------------------

    def fetch(self, url: str) -> ExportableRecord:
        """
        Główne API używane wewnętrznie – obsługuje #fragment (sekcje),
        przycina infoboksy po infobox-full-data itd.

        Merge:
        - serwisy z main,
        - osłona błędów w stylu nowego F1Scraper (network/parse + soft-skip jeśli _handle_scraper_error).
        """
        self.url = url
        base_url, fragment = (url.split("#", 1) + [None])[:2]
        self.url = base_url

        # --- download + obsługa błędów (kompatybilnie z F1Scraper) ---
        try:
            html = self._download()
        except ScraperError as exc:  # type: ignore[misc]
            if self._maybe_handle_scraper_error(exc):
                return {"url": url}
            raise
        except Exception as exc:
            wrapped = self._maybe_wrap_network_error(exc)
            if self._maybe_handle_scraper_error(wrapped):
                return {"url": url}
            raise wrapped from exc

        full_soup = BeautifulSoup(html, "html.parser")

        if not self._is_circuit_like_article(full_soup):
            title = full_soup.title.get_text(strip=True) if full_soup.title else None
            return self.text_utils._prune_nulls(
                {
                    "url": url,
                    "title": title,
                }
            )

        soup = full_soup
        if fragment:
            section = self.section_extractor.extract_section_by_id(full_soup, fragment)
            if section is not None:
                soup = section

        try:
            return self.parse_from_soup(soup)
        except ScraperError as exc:  # type: ignore[misc]
            if self._maybe_handle_scraper_error(exc):
                return {"url": url}
            raise
        except Exception as exc:
            wrapped = self._maybe_wrap_parse_error(exc)
            if self._maybe_handle_scraper_error(wrapped):
                return {"url": url}
            raise wrapped from exc

    def _parse_soup(self, soup: BeautifulSoup) -> list[ExportableRecord]:
        """API bazowej klasy – deleguje do parse_from_soup."""
        return [self.parse_from_soup(soup)]

    def parse_from_soup(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Zwraca znormalizowany infobox + layouts (bez surowego `rows`).

        Od pierwszego wiersza z class="infobox-full-data" w danej tabeli
        infoboksa ignorujemy resztę wierszy (wycinamy je z DOM-u),
        żeby nie mieszać danych z pełnotabelarycznymi statystykami.
        """
        truncated_soup = self._truncate_infobox_after_full_data(soup)

        raw = self.infobox_scraper.parse_from_soup(truncated_soup)

        # layouty parsujemy z pełnej sekcji artykułu
        layout_records = self.layouts_parser.parse_layout_sections(soup)
        return self.entities_parser.with_normalized(raw, layout_records)

    # ------------------------------
    # Helper: przycinanie infoboksa
    # ------------------------------

    def _truncate_infobox_after_full_data(self, soup: BeautifulSoup) -> BeautifulSoup:
        """
        W każdej tabeli infoboksa usuwamy:
        - pierwszy wiersz, który ma klasę `infobox-full-data`
          LUB zawiera komórkę (td/th) z tą klasą,
        - wszystkie kolejne wiersze poniżej.
        """

        def _has_infobox_class(classes: Any) -> bool:
            if not classes:
                return False
            if isinstance(classes, str):
                classes = classes.split()
            return "infobox" in classes

        for table in soup.find_all("table", class_=_has_infobox_class):
            rows: list[Tag] = table.find_all("tr")

            cut_index: Optional[int] = None
            for idx, row in enumerate(rows):
                row_classes = row.get("class") or []
                if isinstance(row_classes, str):
                    row_classes = row_classes.split()

                has_full_on_tr = "infobox-full-data" in row_classes
                has_full_in_cell = (
                    row.find(["td", "th"], class_="infobox-full-data") is not None
                )

                if has_full_on_tr or has_full_in_cell:
                    cut_index = idx
                    break

            if cut_index is not None:
                for r in rows[cut_index:]:
                    r.decompose()

        return soup

    # ------------------------------
    # Pobieranie / sekcje / kategorie
    # ------------------------------

    def _download(self) -> str:
        if not self.url:
            raise ScraperParseError("URL must be set before downloading")
        return self.fetcher.get_text(self.url, timeout=self.timeout)

    def _is_circuit_like_article(self, soup: BeautifulSoup) -> bool:
        """Sprawdza czy artykuł wygląda na tor/tor wyścigowy po kategoriach."""
        cat_div = soup.find("div", id="mw-normal-catlinks")
        if not cat_div:
            return False

        keywords = [
            "circuit",
            "race track",
            "racetrack",
            "speedway",
            "raceway",
            "motor racing",
            "motorsport venue",
        ]
        for a in cat_div.find_all("a"):
            text = a.get_text(strip=True).lower()
            if any(kw in text for kw in keywords):
                return True
        return False

    # ------------------------------
    # Kompatybilne hooki error-handling, bez wymogu miksinów
    # ------------------------------

    def _maybe_handle_scraper_error(self, exc: Exception) -> bool:
        """
        Jeśli bazowy F1Scraper ma mechanizm obsługi błędów (skip/warn),
        to go użyjemy. W przeciwnym razie: nie obsługujemy.
        """
        handler = getattr(self, "_handle_scraper_error", None)
        if callable(handler):
            return bool(handler(exc))
        return False

    def _maybe_wrap_network_error(self, exc: Exception) -> Exception:
        wrapper = getattr(self, "_wrap_network_error", None)
        if callable(wrapper):
            return wrapper(exc)
        return exc

    def _maybe_wrap_parse_error(self, exc: Exception) -> Exception:
        wrapper = getattr(self, "_wrap_parse_error", None)
        if callable(wrapper):
            return wrapper(exc)
        return exc
