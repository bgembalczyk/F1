import re
from typing import List, Dict, Any, Optional

from bs4 import BeautifulSoup


class CircuitInfoboxLayoutsMixin:
    """Logika parsowania sekcji layoutów z infoboksa toru."""

    def _parse_layout_sections(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        table = self._find_infobox(soup)
        if table is None:
            return []

        layouts: List[Dict[str, Any]] = []
        current: Optional[Dict[str, Any]] = None

        for tr in table.find_all("tr"):
            if tr.find_parent("table") is not table:
                continue

            header = tr.find("th", recursive=False)
            data = tr.find("td", recursive=False)

            # Layout header: tylko <th class="infobox-header" colspan=...>
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
                "links": self._extract_links(data),
            }

            if label == "Length":
                current["length_km"] = self._parse_length(cell_row, unit="km")
                current["length_mi"] = self._parse_length(cell_row, unit="mi")
            elif label == "Turns":
                current["turns"] = self._parse_int(cell_row)
            elif label == "Race lap record":
                current["race_lap_record"] = self._parse_lap_record(cell_row)
            elif label == "Surface":
                current["surface"] = self._parse_surface(cell_row)
            elif label == "Banking":
                current["banking"] = self._parse_banking(cell_row)

        return layouts

    def _parse_layout_header(self, text: str) -> tuple[str, Optional[str]]:
        match = re.match(r"^(.*?)(?:\((.*?)\))?$", text)
        if not match:
            return text, None
        name = match.group(1).strip()
        years = match.group(2).strip() if match.group(2) else None
        return name, years
