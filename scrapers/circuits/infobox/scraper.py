from __future__ import annotations

from typing import Any, Dict, Optional

from bs4 import BeautifulSoup, Tag

from scrapers.base.infobox.scraper import WikipediaInfoboxScraper
from scrapers.base.mixins.wiki_sections import WikipediaSectionByIdMixin
from scrapers.base.options import ScraperOptions, init_scraper_options
from scrapers.base.scraper import F1Scraper
from scrapers.base.types import ExportableRecord
from scrapers.base.errors import ScraperParseError
from scrapers.circuits.helpers.article_validation import is_circuit_like_article
from scrapers.circuits.infobox.services.additional_info import (
    CircuitAdditionalInfoParser,
)
from scrapers.circuits.infobox.services.entities import CircuitEntitiesParser
from scrapers.circuits.infobox.services.entity_parsing import CircuitEntityParser
from scrapers.circuits.infobox.services.geo import CircuitGeoParser
from scrapers.circuits.infobox.services.history import CircuitHistoryParser
from scrapers.circuits.infobox.services.lap_record import CircuitLapRecordParser
from scrapers.circuits.infobox.services.layouts import CircuitLayoutsParser
from scrapers.circuits.infobox.services.specs import CircuitSpecsParser
from scrapers.circuits.infobox.services.text_utils import InfoboxTextUtils


class F1CircuitInfoboxScraper(F1Scraper):
    """Parser infoboksów torów F1 z heurystykami pod typowe pola."""

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
    ) -> None:
        options = init_scraper_options(options)

        # Zapewniamy fetcher (spójnie z resztą repo).
        # HtmlFetcher jest config-driven, więc tworzymy go bez “legacy” parametrów.
        options.with_fetcher()

        super().__init__(options=options)

        # Dla czytelności (F1Scraper i tak to trzyma)
        self.fetcher = options.fetcher
        self.policy = options.to_http_policy()
        self.timeout = self.policy.timeout

        # WikipediaInfoboxScraper w stylu "main": przez ScraperOptions + fetcher
        self.infobox_scraper = WikipediaInfoboxScraper(
            options=ScraperOptions(
                fetcher=self.fetcher,
                policy=self.policy,
            ),
        )

        # --- Serwisy ---
        self.section_extractor = WikipediaSectionByIdMixin()
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

    def scrape_url(self, url: str) -> ExportableRecord:
        """
        Główne API – pobiera i parsuje infobox z podanego URL.
        Obsługuje #fragment (sekcje), przycina infoboksy po infobox-full-data itd.

        Merge:
        - serwisy z main,
        - osłona błędów w stylu nowego F1Scraper (network/parse + soft-skip jeśli _handle_scraper_error).
        """
        self.url = url
        base_url, fragment = (url.split("#", 1) + [None])[:2]
        self.url = base_url

        def _parse_full(full_soup: BeautifulSoup) -> ExportableRecord:
            if not is_circuit_like_article(full_soup):
                title = (
                    full_soup.title.get_text(strip=True) if full_soup.title else None
                )
                return self.text_utils.prune_nulls(
                    {
                        "url": url,
                        "title": title,
                    }
                )

            soup = full_soup
            if fragment:
                section = self.section_extractor.extract_section_by_id(
                    full_soup, fragment
                )
                if section is not None:
                    soup = section

            return self.parse_from_soup(soup)

        result = self.run_with_error_handling(
            lambda: self._download(),
            _parse_full,
            base_url,
        )
        return result or {"url": url}

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

    @staticmethod
    def _truncate_infobox_after_full_data(soup: BeautifulSoup) -> BeautifulSoup:
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

    # ------------------------------
