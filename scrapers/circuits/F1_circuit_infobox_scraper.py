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
        """Zwraca znormalizowany infobox + layouts (bez surowego `rows`)."""
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

        used_keys = {
            "Location",
            "Coordinates",
            "FIA Grade",
            "Length",
            "Turns",
            "Race lap record",
            "Opened",
            "Closed",
            "Former names",
            "Owner",
            # nowe znormalizowane pola:
            "Operator",
            "Capacity",
            "Broke ground",
            "Built",
            "Construction cost",
            "Architect",
            "Website",
            "Banking",
            "Area",
        }

        normalized: Dict[str, Any] = {"name": raw.get("title"), "location": self._parse_location(rows.get("Location")),
                                      "coordinates": self._parse_coordinates(rows.get("Coordinates")), "specs": {
                "fia_grade": self._parse_int(rows.get("FIA Grade")),
                "length_km": self._parse_length(rows.get("Length"), unit="km"),
                "length_mi": self._parse_length(rows.get("Length"), unit="mi"),
                "turns": self._parse_int(rows.get("Turns")),
                "capacity": self._parse_capacity(rows.get("Capacity")),
                "construction_cost": self._parse_construction_cost(
                    rows.get("Construction cost")
                ),
                "banking": self._parse_banking(rows.get("Banking")),
                "area": self._parse_area(rows.get("Area")),
            }, "history": self._parse_history(rows), "operator": self._parse_linked_entity(rows.get("Operator")),
                                      "architect": self._parse_linked_entity(rows.get("Architect")),
                                      "website": self._parse_website(rows.get("Website"))}

        # operator / architect jako pola "główne"

        extra_fields = self._collect_additional_info(rows, used_keys)
        if extra_fields:
            normalized["additional_info"] = extra_fields

        normalized = self._prune_nulls(normalized)

        result: Dict[str, Any] = dict(raw or {})
        # nie trzymamy surowych rows
        result.pop("rows", None)

        if layout_records:
            result["layouts"] = self._prune_nulls(layout_records)

        existing_norm = result.get("normalized")
        if isinstance(existing_norm, dict):
            existing_norm.update(normalized)
            result["normalized"] = existing_norm
        else:
            result["normalized"] = normalized

        return self._prune_nulls(result)

    # ------------------------------
    # Helpery parsujące pola
    # ------------------------------

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

        return components or None

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
        """Parsyje daty typu YYYY-MM-DD, YYYY-MM, YYYY i zwraca też listę lat."""
        if not row:
            return None
        text = self._get_text(row) or ""
        if not text:
            return None

        iso_full = re.findall(r"\d{4}-\d{2}-\d{2}", text)
        iso_month = re.findall(r"\d{4}-\d{2}", text)
        years = re.findall(r"\b(1[89]\d{2}|20\d{2})\b", text)

        iso_dates: List[str] = []
        if iso_full:
            iso_dates = iso_full
        elif iso_month:
            iso_dates = iso_month

        return {
            "text": text or None,
            "iso_dates": iso_dates or None,
            "years": years or None,
        }

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

    def _parse_capacity(self, row: Optional[Dict[str, Any]]) -> Optional[Dict[str, int]]:
        """Capacity: rozbicie na total / seating z tekstu typu '~125,000 (44,000 seating)'."""
        if not row:
            return None
        text = self._get_text(row) or ""
        if not text:
            return None

        # usuń przypisy [1], [2] itd.
        text = re.sub(r"\[\d+]", "", text)
        numbers = re.findall(r"[\d,]+", text)
        if not numbers:
            return None

        def _to_int(s: str) -> int:
            return int(s.replace(",", "").replace(" ", ""))

        vals = [_to_int(n) for n in numbers]
        result: Dict[str, int] = {}
        if len(vals) >= 1:
            result["total"] = vals[0]
        if len(vals) >= 2:
            result["seating"] = vals[1]
        return result or None

    def _parse_construction_cost(self, row: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Construction cost: amount + currency (+ opcjonalna skala)."""
        if not row:
            return None
        text = self._get_text(row) or ""
        if not text:
            return None

        text_clean = re.sub(r"\[\d+]", "", text)

        symbol_map = {
            "€": "EUR",
            "$": "USD",
            "£": "GBP",
            "¥": "JPY",
        }

        currency: Optional[str] = None
        for symbol, code in symbol_map.items():
            if symbol in text_clean:
                currency = code
                break

        if currency is None:
            match_code = re.search(r"\b(EUR|USD|GBP|JPY|AUD|CAD|PLN|CHF)\b", text_clean)
            if match_code:
                currency = match_code.group(1)

        amount_match = re.search(r"([\d.,]+)", text_clean)
        if not amount_match and not currency:
            return None

        amount: Optional[float] = None
        if amount_match:
            try:
                amount = float(amount_match.group(1).replace(",", ""))
            except ValueError:
                amount = None

        scale_match = re.search(
            r"\b(million|billion|thousand|mln|bn|k)\b", text_clean, flags=re.IGNORECASE
        )
        scale = scale_match.group(1).lower() if scale_match else None

        result: Dict[str, Any] = {
            "amount": amount,
            "currency": currency,
        }
        if scale:
            result["scale"] = scale
        result["text"] = text_clean.strip() or None
        return self._prune_nulls(result)

    def _parse_banking(self, row: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Banking: liczba + jednostka + opcjonalna notka."""
        if not row:
            return None
        text = self._get_text(row) or ""
        if not text:
            return None

        angle_match = re.search(r"([\d.,]+)\s*°", text)
        percent_match = re.search(r"([\d.,]+)\s*%", text)

        value: Optional[float] = None
        unit: Optional[str] = None

        if angle_match:
            value = float(angle_match.group(1).replace(",", "."))
            unit = "deg"
        elif percent_match:
            value = float(percent_match.group(1).replace(",", "."))
            unit = "percent"

        result: Dict[str, Any] = {}
        if value is not None:
            result["value"] = value
        if unit:
            result["unit"] = unit

        # reszta tekstu jako notka
        cleaned = text
        for m in (angle_match, percent_match):
            if m:
                cleaned = cleaned.replace(m.group(0), "")
        cleaned = cleaned.strip(" ()-;,")
        if cleaned:
            result["note"] = cleaned

        return result or None

    def _parse_area(self, row: Optional[Dict[str, Any]]) -> Optional[Dict[str, float]]:
        """Area: np. '277 acres (112 ha)' -> acres + hectares."""
        if not row:
            return None
        text = self._get_text(row) or ""
        if not text:
            return None

        acres_match = re.search(r"([\d.,]+)\s*acres?", text, flags=re.IGNORECASE)
        ha_match = re.search(r"([\d.,]+)\s*ha\b", text, flags=re.IGNORECASE)

        def _to_float(s: str) -> float:
            return float(s.replace(",", "."))

        result: Dict[str, float] = {}
        if acres_match:
            result["acres"] = _to_float(acres_match.group(1))
        if ha_match:
            result["hectares"] = _to_float(ha_match.group(1))

        return result or None

    def _parse_history(self, rows: Dict[str, Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        events: List[Dict[str, Any]] = []

        def _dates_to_list(d: Dict[str, Any]) -> List[str]:
            if not d:
                return []
            return (d.get("iso_dates") or d.get("years") or [])  # type: ignore[return-value]

        opened_dates = self._parse_dates(rows.get("Opened")) or {}
        for idx, date in enumerate(_dates_to_list(opened_dates)):
            events.append(
                {
                    "event": "opened" if idx == 0 else "reopened",
                    "date": date,
                }
            )

        closed_dates = self._parse_dates(rows.get("Closed")) or {}
        for date in _dates_to_list(closed_dates):
            events.append({"event": "closed", "date": date})

        broke_ground_dates = self._parse_dates(rows.get("Broke ground")) or {}
        for date in _dates_to_list(broke_ground_dates):
            events.append({"event": "broke_ground", "date": date})

        built_dates = self._parse_dates(rows.get("Built")) or {}
        for date in _dates_to_list(built_dates):
            events.append({"event": "built", "date": date})

        events = sorted(events, key=lambda e: e.get("date") or "")

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

        for layout in layouts:
            if layout.get("race_lap_record"):
                records.append(self._prune_nulls(layout))

        base_record = self._parse_lap_record(base_record_row)
        if base_record and not self._lap_record_exists(base_record, records):
            records.append({"race_lap_record": base_record})

        return records

    def _prune_nulls(self, data: Any) -> Any:
        if isinstance(data, dict):
            pruned_dict = {}
            for key, value in data.items():
                cleaned = self._prune_nulls(value)
                if cleaned is None:
                    continue
                if isinstance(cleaned, (dict, list)) and len(cleaned) == 0:
                    continue
                pruned_dict[key] = cleaned
            return pruned_dict

        if isinstance(data, list):
            pruned_list = []
            for value in data:
                cleaned = self._prune_nulls(value)
                if cleaned is None:
                    continue
                if isinstance(cleaned, (dict, list)) and len(cleaned) == 0:
                    continue
                pruned_list.append(cleaned)
            return pruned_list

        return data

    def _lap_record_exists(
            self, candidate: Dict[str, Any], records: List[Dict[str, Any]]
    ) -> bool:
        for record in records:
            if self._same_lap_record(candidate, record.get("race_lap_record")):
                return True
        return False

    def _same_lap_record(
            self, left: Optional[Dict[str, Any]], right: Optional[Dict[str, Any]]
    ) -> bool:
        if not left or not right:
            return False

        def _text(obj: Optional[Dict[str, Any]]) -> Optional[str]:
            if not obj:
                return None
            return obj.get("text") if isinstance(obj, dict) else None

        return (
                left.get("time") == right.get("time")
                and _text(left.get("driver")) == _text(right.get("driver"))
                and _text(left.get("car")) == _text(right.get("car"))
                and left.get("year") == right.get("year")
                and left.get("series") == right.get("series")
        )

    def _parse_linked_entity(
            self, row: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any] | str]:
        """Pola typu Operator / Architect – link jeśli jest, inaczej czysty tekst."""
        if not row:
            return None
        text = self._get_text(row) or ""
        links = row.get("links") or []
        if not links:
            return text or None

        link = self._find_link(text, links) or links[0]
        url = link.get("url")
        if not url:
            return text or None
        return {"text": text, "url": url}

    def _parse_website(self, row: Optional[Dict[str, Any]]) -> Optional[str]:
        """Website jako URL (z linku, jeśli jest)."""
        if not row:
            return None
        text = self._get_text(row) or ""
        links = row.get("links") or []
        if links:
            return links[0].get("url") or text or None
        return text or None

    def _collect_additional_info(
            self, rows: Dict[str, Dict[str, Any]], used_keys: set[str]
    ) -> Optional[Dict[str, Any]]:
        """Dodatkowe pola – tekst + ewentualna lista wartości z linkami."""
        additional: Dict[str, Any] = {}

        for key, row in rows.items():
            if key in used_keys:
                continue

            text = self._get_text(row)
            if not text:
                continue

            info: Dict[str, Any] = {"text": text}
            links = row.get("links") or []

            # jeżeli to jest wyliczenie, spróbuj rozbić na listę wartości
            parts = [p.strip() for p in re.split(r";|,|/", text) if p.strip()]
            if len(parts) > 1:
                values: List[Any] = []
                for part in parts:
                    link = self._find_link(part, links)
                    if link:
                        values.append({"text": part, "url": link.get("url")})
                    else:
                        values.append(part)
                info["values"] = values
            elif links:
                info["links"] = links

            additional[key] = info

        return additional or None

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
