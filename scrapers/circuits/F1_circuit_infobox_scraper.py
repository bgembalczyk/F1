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
        return self._with_normalized(raw)

    # ------------------------------
    # Normalizacja pól
    # ------------------------------

    def _with_normalized(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        rows: Dict[str, Dict[str, Any]] = raw.get("rows", {}) if raw else {}

        normalized = {
            "name": raw.get("title"),
            "location": self._parse_location(rows.get("Location")),
            "coordinates": self._parse_coordinates(rows.get("Coordinates")),
            "specs": {
                "fia_grade": self._get_text(rows.get("FIA Grade")),
                "length_km": self._parse_length(rows.get("Length"), unit="km"),
                "length_mi": self._parse_length(rows.get("Length"), unit="mi"),
                "turns": self._parse_int(rows.get("Turns")),
            },
            "history": {
                "opened": self._parse_dates(rows.get("Opened")),
                "closed": self._parse_dates(rows.get("Closed")),
                "former_names": self._split_simple_list(rows.get("Former names")),
                "owner": self._get_text(rows.get("Owner")),
            },
            "events": self._parse_events(rows.get("Major events")),
            "records": {
                "race_lap": self._parse_lap_record(rows.get("Race lap record")),
            },
            "raw_rows": rows,
        }

        return {"raw": raw, "normalized": normalized}

    def _get_text(self, row: Optional[Dict[str, Any]]) -> Optional[str]:
        if not row:
            return None
        text = row.get("text")
        return text.strip() if isinstance(text, str) else None

    def _parse_location(self, row: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not row:
            return None
        text = self._get_text(row) or ""
        parts = [part.strip(" ,") for part in re.split(r",|\u00b7|/|;", text) if part.strip(" ,")]
        return {"raw": text or None, "parts": parts or None, "links": row.get("links", [])}

    def _parse_coordinates(self, row: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not row:
            return None
        return {"raw": self._get_text(row), "links": row.get("links", [])}

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
        return {"raw": text or None, "iso_dates": iso_dates or None}

    def _split_simple_list(self, row: Optional[Dict[str, Any]]) -> Optional[List[str]]:
        if not row:
            return None
        text = self._get_text(row) or ""
        parts = [p.strip() for p in re.split(r";|,|/", text) if p.strip()]
        return parts or None

    def _parse_events(self, row: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not row:
            return None
        text = self._get_text(row) or ""
        sections = self._split_sections(text)

        parsed_sections: Dict[str, List[str]] = {}
        for name, content in sections.items():
            events = re.findall(r"[^()]+\([^)]*\)", content)
            if not events:
                events = [p.strip(" ;") for p in re.split(r"(?<=\))\s+|\s{2,}", content) if p.strip(" ;")]
            parsed_sections[name] = events

        return {"raw": text or None, **parsed_sections}

    def _split_sections(self, text: str) -> Dict[str, str]:
        pattern = re.compile(r"\b(Current|Future|Former):")
        matches = list(pattern.finditer(text))
        if not matches:
            return {"unspecified": text.strip()}

        sections: Dict[str, str] = {}
        for idx, match in enumerate(matches):
            start = match.end()
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
            section_text = text[start:end].strip()
            sections[match.group(1).lower()] = section_text
        return sections

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
            "raw": text or None,
            "time": time_match.group(0) if time_match else None,
        }

        if details:
            record.update(
                {
                    "driver": details[0] if len(details) >= 1 else None,
                    "car": details[1] if len(details) >= 2 else None,
                    "year": details[2] if len(details) >= 3 else None,
                    "series": details[3] if len(details) >= 4 else None,
                }
            )

        return record
