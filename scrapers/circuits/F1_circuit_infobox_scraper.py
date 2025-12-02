from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

import requests

from bs4 import BeautifulSoup

from scrapers.base.wiki_infobox_scraper import WikipediaInfoboxScraper


from scrapers.base.F1_scraper import F1Scraper


class F1CircuitInfoboxScraper(F1Scraper, WikipediaInfoboxScraper):
    """Parser infoboksów torów F1 z heurystykami pod typowe pola."""

    def __init__(
        self,
        *,
        timeout: int = 10,
        include_urls: bool = True,
        session: Optional[requests.Session] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        F1Scraper.__init__(self, include_urls=include_urls, session=session, headers=headers)
        WikipediaInfoboxScraper.__init__(self, timeout=timeout)
        self.url: str = ""

    def fetch(self, url: str) -> Dict[str, Any]:
        self.url = url
        html = self._download()
        soup = BeautifulSoup(html, "html.parser")
        return self.parse_from_soup(soup)

    def _download(self) -> str:
        if not self.url:
            raise ValueError("URL must be set before downloading")
        response = self.session.get(self.url, timeout=self.timeout)
        response.raise_for_status()
        return response.text

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """API bazowej klasy – deleguje do parse_from_soup."""
        return [self.parse_from_soup(soup)]

    def parse_from_soup(self, soup: BeautifulSoup) -> Dict[str, Any]:
        raw = super().parse_from_soup(soup)
        layout_records = self._parse_layout_sections(soup)
        return self._with_normalized(raw, layout_records)

    # ------------------------------
    # Normalizacja pól
    # ------------------------------

    def _with_normalized(
        self, raw: Dict[str, Any], layout_records: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        rows: Dict[str, Dict[str, Any]] = raw.get("rows", {}) if raw else {}

        normalized = {
            "name": raw.get("title"),
            "location": self._parse_location(rows.get("Location")),
            "coordinates": self._parse_coordinates(rows.get("Coordinates")),
            "specs": {
                "fia_grade": self._parse_int(rows.get("FIA Grade")),
                "length_km": self._parse_length(rows.get("Length"), unit="km"),
                "length_mi": self._parse_length(rows.get("Length"), unit="mi"),
                "turns": self._parse_int(rows.get("Turns")),
            },
            "history": self._parse_history(rows),
            "records": self._merge_records(
                rows.get("Race lap record"), layout_records or []
            ),
        }

        return normalized

    def _get_text(self, row: Optional[Dict[str, Any]]) -> Optional[str]:
        if not row:
            return None
        text = row.get("text")
        return text.strip() if isinstance(text, str) else None

    def _parse_location(self, row: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not row:
            return None
        text = self._get_text(row) or ""
        parts = [
            part.strip(" ,") for part in re.split(r",|\u00b7|/|;", text) if part.strip(" ,")
        ]

        components: Dict[str, Optional[Dict[str, Any]]] = {}
        links = row.get("links") or []
        for idx, part in enumerate(parts):
            key = f"localisation{idx + 1}"
            link = self._find_link(part, links)
            components[key] = {
                "text": part,
                "link": link,
            }

        return {
            "text": text or None,
            "parts": parts or None,
            "components": components,
            "links": row.get("links") or None,
        }

    def _parse_coordinates(self, row: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not row:
            return None
        text = self._get_text(row) or ""
        return self._parse_position(text)

    def _parse_position(self, text: str) -> Optional[Dict[str, float]]:
        if not text:
            return None

        decimal_match = re.search(r"(-?\d+(?:\.\d+)?);\s*(-?\d+(?:\.\d+)?)", text)
        if decimal_match:
            return {
                "lat": float(decimal_match.group(1)),
                "lon": float(decimal_match.group(2)),
            }

        parts = re.findall(r"([NSWE]?)(-?\d+(?:\.\d+)?)", text)
        if len(parts) >= 2:
            lat_dir, lat_val = parts[0]
            lon_dir, lon_val = parts[1]
            lat = float(lat_val)
            lon = float(lon_val)
            if lat_dir.upper() == "S":
                lat = -lat
            if lon_dir.upper() == "W":
                lon = -lon
            return {"lat": lat, "lon": lon}

        return None

    def _parse_length(self, row: Optional[Dict[str, Any]], *, unit: str) -> Optional[float]:
        if not row:
            return None
        text = self._get_text(row) or ""
        match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*" + re.escape(unit), text)
        return float(match.group(1)) if match else None

    def _parse_int(self, row: Optional[Dict[str, Any]]) -> Optional[int]:
        if not row:
            return None
        text = self._get_text(row) or ""
        match = re.search(r"\d+", text)
        return int(match.group()) if match else None

    def _parse_dates(self, row: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not row:
            return None
        text = self._get_text(row) or ""
        iso_dates = re.findall(r"\d{4}-\d{2}-\d{2}", text)
        return {"text": text or None, "iso_dates": iso_dates or None}

    def _split_simple_list(self, row: Optional[Dict[str, Any]]) -> Optional[List[str]]:
        if not row:
            return None
        text = self._get_text(row) or ""
        parts = [p.strip() for p in re.split(r";|,|/", text) if p.strip()]
        return parts or None

    def _parse_lap_record(self, row: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not row:
            return None
        text = self._get_text(row) or ""
        time_match = re.search(r"\d+:\d{2}\.\d{3}", text)
        details_match = re.search(r"\(([^)]*)\)", text)

        details: List[str] = []
        if details_match:
            details = [part.strip() for part in details_match.group(1).split(",") if part.strip()]

        record: Dict[str, Any] = {
            "time": time_match.group(0) if time_match else None,
        }

        if details:
            driver_text = details[0] if len(details) >= 1 else None
            car_text = details[1] if len(details) >= 2 else None
            record.update(
                {
                    "driver": self._with_link(driver_text, row.get("links")),
                    "car": self._with_link(car_text, row.get("links")),
                    "year": details[2] if len(details) >= 3 else None,
                    "series": details[3] if len(details) >= 4 else None,
                }
            )

        return record

    def _parse_history(self, rows: Dict[str, Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        events: List[Dict[str, Any]] = []

        opened_dates = self._parse_dates(rows.get("Opened")) or {}
        for idx, date in enumerate(opened_dates.get("iso_dates") or []):
            events.append({
                "event": "opened" if idx == 0 else "reopened",
                "date": date,
            })

        closed_dates = self._parse_dates(rows.get("Closed")) or {}
        for date in closed_dates.get("iso_dates") or []:
            events.append({"event": "closed", "date": date})

        events = sorted(
            events, key=lambda e: e.get("date") or ""
        )

        history = {
            "events": events or None,
            "former_names": self._split_simple_list(rows.get("Former names")),
            "owner": self._get_text(rows.get("Owner")),
        }

        return history

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

            if header and header.get("colspan"):
                layout_name, years = self._parse_layout_header(header.get_text(" ", strip=True))
                current = {
                    "layout": layout_name,
                    "years": years,
                    "length_km": None,
                    "length_mi": None,
                    "turns": None,
                    "race_lap_record": None,
                }
                layouts.append(current)
                continue

            if current is None or not header or not data:
                continue

            label = header.get_text(" ", strip=True)
            cell_row = {"text": data.get_text(" ", strip=True), "links": self._extract_links(data)}

            if label == "Length":
                current["length_km"] = self._parse_length(cell_row, unit="km")
                current["length_mi"] = self._parse_length(cell_row, unit="mi")
            elif label == "Turns":
                current["turns"] = self._parse_int(cell_row)
            elif label == "Race lap record":
                current["race_lap_record"] = self._parse_lap_record(cell_row)

        return layouts

    def _parse_layout_header(self, text: str) -> tuple[str, Optional[str]]:
        match = re.match(r"^(.*?)(?:\((.*?)\))?$", text)
        if not match:
            return text, None
        name = match.group(1).strip()
        years = match.group(2).strip() if match.group(2) else None
        return name, years

    def _merge_records(
        self, base_record_row: Optional[Dict[str, Any]], layouts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []

        base_record = self._parse_lap_record(base_record_row)
        if base_record:
            records.append({"race_lap_record": base_record})

        for layout in layouts:
            if layout.get("race_lap_record"):
                records.append(self._prune_nulls(layout))

        return records

    def _prune_nulls(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {k: v for k, v in data.items() if v is not None}

    def _find_link(
        self, text: Optional[str], links: List[Dict[str, str]]
    ) -> Optional[Dict[str, str]]:
        if not text:
            return None
        for link in links:
            if link.get("text", "").strip().lower() == text.strip().lower():
                return link
        return None

    def _with_link(
        self, text: Optional[str], links: Optional[List[Dict[str, str]]]
    ) -> Optional[Dict[str, Any]]:
        if text is None:
            return None
        link = self._find_link(text, links or [])
        return {"text": text, "url": link.get("url") if link else None}
