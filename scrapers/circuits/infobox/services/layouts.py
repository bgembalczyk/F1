import re
from collections.abc import Callable
from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.error_handler import ErrorHandler
from scrapers.base.infobox.scraper import WikipediaInfoboxScraper
from scrapers.base.parsers.safe_parser_mixin import SafeParserMixin
from scrapers.circuits.infobox.schema import CIRCUIT_INFOBOX_SCHEMA
from scrapers.circuits.infobox.services.lap_record import CircuitLapRecordParser
from scrapers.circuits.infobox.services.specs import CircuitSpecsParser
from scrapers.circuits.infobox.services.text_utils import InfoboxTextUtils


class CircuitLayoutsParser(SafeParserMixin):
    """Logika parsowania sekcji layoutów z infoboksa toru."""

    def __init__(
        self,
        *,
        infobox_scraper: WikipediaInfoboxScraper,
        text_utils: InfoboxTextUtils,
        lap_record_parser: CircuitLapRecordParser,
        specs_parser: CircuitSpecsParser,
        error_handler: ErrorHandler | None = None,
        url_provider: Callable[[], str | None] | None = None,
    ) -> None:
        self.infobox_scraper = infobox_scraper
        self.text_utils = text_utils
        self.lap_record_parser = lap_record_parser
        self.specs_parser = specs_parser
        self.schema = CIRCUIT_INFOBOX_SCHEMA
        self.error_handler = error_handler or ErrorHandler()
        self._url_provider = url_provider

    @staticmethod
    def _is_layout_header(row_header: Tag) -> bool:
        classes = row_header.get("class", [])
        return bool(row_header.get("colspan") and "infobox-header" in classes)

    def _apply_layout_field(
        self,
        current: dict[str, Any],
        label: str,
        cell_row: dict[str, Any],
    ) -> None:
        if label == "length":
            current["length_km"] = self._safe_parse(
                self.text_utils.parse_length,
                cell_row,
                unit="km",
            )
            current["length_mi"] = self._safe_parse(
                self.text_utils.parse_length,
                cell_row,
                unit="mi",
            )
            return

        if label == "turns":
            current["turns"] = self._safe_parse(self.text_utils.parse_int, cell_row)
            return

        if label == "race_lap_record":
            current["race_lap_record"] = self._safe_parse(
                self.lap_record_parser.parse_lap_record,
                cell_row,
            )
            return

        if label == "surface":
            current["surface"] = self._safe_parse(
                self.specs_parser.parse_surface,
                cell_row,
            )
            return

        if label == "banking":
            current["banking"] = self._safe_parse(
                self.specs_parser.parse_banking,
                cell_row,
            )

    def parse_layout_sections(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        table = self.infobox_scraper.parser.find_infobox(soup)
        if table is None:
            return []

        layouts: list[dict[str, Any]] = []
        current: dict[str, Any] | None = None

        for tr in table.find_all("tr"):
            if tr.find_parent("table") is not table:
                continue

            header = tr.find("th", recursive=False)
            data = tr.find("td", recursive=False)

            if header and self._is_layout_header(header):
                layout_name, years = self._parse_layout_header(
                    header.get_text(" ", strip=True),
                )
                current = {
                    "layout": layout_name,
                    "years": years,
                    "length_km": None,
                    "length_mi": None,
                    "turns": None,
                    "race_lap_record": None,
                    "surface": None,
                    "banking": None,
                }
                layouts.append(current)
                continue

            if current is None or not header or not data:
                continue

            label = self.schema.normalize_label(header.get_text(" ", strip=True))
            cell_row = {
                "text": data.get_text(" ", strip=True),
                "links": self.infobox_scraper.parser.extract_links(data),
            }
            self._apply_layout_field(current, label, cell_row)

        return layouts

    @staticmethod
    def _parse_layout_header(text: str) -> tuple[str, str | None]:
        match = re.match(r"^(.*?)(?:\((.*?)\))?$", text)
        if not match:
            return text, None
        name = match.group(1).strip()
        years = match.group(2).strip() if match.group(2) else None
        return name, years
