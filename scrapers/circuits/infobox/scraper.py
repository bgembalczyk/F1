from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.error_handler import ErrorHandler
from scrapers.base.infobox.field_mapper import InfoboxFieldMapper
from scrapers.base.infobox.scraper import WikipediaInfoboxScraper
from scrapers.base.infobox.scraper import parse_infobox_from_soup
from scrapers.base.logging import get_logger
from scrapers.base.options import ScraperOptions
from scrapers.base.types import ExportableRecord
from scrapers.circuits.infobox.schema import CIRCUIT_INFOBOX_SCHEMA
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
from scrapers.wiki.parsers.elements.infobox import InfoboxParser


class F1CircuitInfoboxParser(InfoboxParser):
    """Parser infoboksów torów F1 z heurystykami pod typowe pola."""

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        url: str = "",
    ) -> None:
        options = options or ScraperOptions()

        self.logger = get_logger(self.__class__.__name__)
        self._error_handler = ErrorHandler(
            logger=self.logger,
            debug_dir=options.debug_dir,
            error_report_enabled=options.error_report,
            run_id=options.run_id,
        )
        self._run_id = options.run_id

        # WikipediaInfoboxScraper: używamy tylko parsera i mappera (bez HTTP)
        self.infobox_scraper = WikipediaInfoboxScraper(
            mapper=InfoboxFieldMapper(
                schema=CIRCUIT_INFOBOX_SCHEMA,
                logger=self.logger,
                context="circuit.infobox",
            ),
        )

        # --- Serwisy ---
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
            error_handler=self._error_handler,
            url_provider=lambda: self.url,
        )

        self.layouts_parser = CircuitLayoutsParser(
            infobox_scraper=self.infobox_scraper,
            text_utils=self.text_utils,
            lap_record_parser=self.lap_record_parser,
            specs_parser=self.specs_parser,
            error_handler=self._error_handler,
            url_provider=lambda: self.url,
        )

        self.url: str = url

    # ------------------------------
    # Publiczne API
    # ------------------------------

    def parse(self, soup: BeautifulSoup) -> list[ExportableRecord]:
        return [self._parse_infobox(soup)]

    def _parse_infobox(self, soup: BeautifulSoup) -> dict[str, Any]:
        """
        Zwraca znormalizowany infobox + layouts (bez surowego `rows`).

        Od pierwszego wiersza z class="infobox-full-data" w danej tabeli
        infoboksa ignorujemy resztę wierszy (wycinamy je z DOM-u),
        żeby nie mieszać danych z pełnotabelarycznymi statystykami.
        """
        truncated_soup = self._truncate_infobox_after_full_data(soup)

        self.infobox_scraper.run_id = self._run_id
        self.infobox_scraper.url = self.url
        raw = parse_infobox_from_soup(self.infobox_scraper, truncated_soup)

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

            cut_index: int | None = None
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
