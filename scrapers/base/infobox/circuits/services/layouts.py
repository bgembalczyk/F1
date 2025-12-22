import re
from typing import List, Dict, Any, Optional

from bs4 import BeautifulSoup

from scrapers.base.infobox.circuits.services.lap_record import CircuitLapRecordParser
from scrapers.base.infobox.circuits.services.specs import CircuitSpecsParser
from scrapers.base.infobox.circuits.services.text_utils import InfoboxTextUtils
from scrapers.base.infobox.scraper import WikipediaInfoboxScraper


class CircuitLayoutsParser:
    """Logika parsowania sekcji layoutów z infoboksa toru."""

    def __init__(
        self,
        *,
        infobox_scraper: WikipediaInfoboxScraper,
        text_utils: InfoboxTextUtils,
        lap_record_parser: CircuitLapRecordParser,
        specs_parser: CircuitSpecsParser,
    ) -> None:
        self.infobox_scraper = infobox_scraper
        self.text_utils = text_utils
        self.lap_record_parser = lap_record_parser
        self.specs_parser = specs_parser

    def parse_layout_sections(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        table = self.infobox_scraper.parser.find_infobox(soup)
        if table is None:
            return []

        layouts: List[Dict[str, Any]] = []
        current: Optional[Dict[str, Any]] = None

        for tr in table.find_all("tr"):
            if tr.find_parent("table") is not table:
                continue

            header = tr.find("th", recursive=False)
            data = tr.find("td", recursive=False)

            if header and header.get("colspan"):
                classes = header.get("class", [])
                if "infobox-header" in classes:
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

            label = header.get_text(" ", strip=True)
            cell_row = {
                "text": data.get_text(" ", strip=True),
                "links": self.infobox_scraper.parser.extract_links(data),
            }

            if label == "Length":
                current["length_km"] = self.text_utils.parse_length(
                    cell_row, unit="km"
                )
                current["length_mi"] = self.text_utils.parse_length(
                    cell_row, unit="mi"
                )
            elif label == "Turns":
                current["turns"] = self.text_utils.parse_int(cell_row)
            elif label == "Race lap record":
                current["race_lap_record"] = self.lap_record_parser.parse_lap_record(
                    cell_row
                )
            elif label == "Surface":
                current["surface"] = self.specs_parser.parse_surface(cell_row)
            elif label == "Banking":
                current["banking"] = self.specs_parser.parse_banking(cell_row)

        return layouts

    @staticmethod
    def _parse_layout_header(text: str) -> tuple[str, Optional[str]]:
        match = re.match(r"^(.*?)(?:\((.*?)\))?$", text)
        if not match:
            return text, None
        name = match.group(1).strip()
        years = match.group(2).strip() if match.group(2) else None
        return name, years
