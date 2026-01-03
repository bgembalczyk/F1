import re
from typing import Optional, Dict, Any, List

from models.records.link import LinkRecord
from scrapers.base.helpers.text_normalization import clean_infobox_text
from scrapers.circuits.infobox.services.constants import LOCATION_STOPWORDS
from scrapers.circuits.infobox.services.text_utils import InfoboxTextUtils


class CircuitGeoParser(InfoboxTextUtils):
    """Parsowanie lokalizacji, współrzędnych, powierzchni."""

    @staticmethod
    def _split_plain_segment(segment: str) -> List[str]:
        """Dzieli segment tekstu na części rozdzielone przecinkami, ukośnikami itp."""
        segment_parts: List[str] = []
        for raw_part in re.split(r"[,·/;]", segment):
            cleaned_part = raw_part.strip(" ,")
            if not cleaned_part:
                continue
            if cleaned_part.lower() in LOCATION_STOPWORDS:
                continue
            segment_parts.append(cleaned_part)
        return segment_parts

    def parse_location(self, row: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not row:
            return None

        text = clean_infobox_text(row.get("text")) or ""
        links: List[LinkRecord] = row.get("links") or []

        components: List[Dict[str, Any]] = []
        cursor = 0

        for link in links:
            link_text = (link.get("text") or "").strip()
            if not link_text:
                continue

            idx = text.find(link_text, cursor)
            if idx == -1:
                continue

            before = text[cursor:idx]
            for part in self._split_plain_segment(before):
                components.append({"text": part})

            components.append(
                {
                    "text": link_text,
                    "link": {
                        "text": link_text,
                        "url": link.get("url"),
                    },
                }
            )
            cursor = idx + len(link_text)

        tail = text[cursor:]
        for part in self._split_plain_segment(tail):
            components.append({"text": part})

        if not components:
            return None

        filtered_components: List[Dict[str, Any]] = []
        for comp in components:
            txt = (comp.get("text") or "").strip()
            if not txt or txt.lower() in LOCATION_STOPWORDS:
                continue
            filtered_components.append(comp)

        if not filtered_components:
            return None

        result: Dict[str, Any] = {}
        for idx, comp in enumerate(filtered_components, start=1):
            key = f"localisation{idx}"
            result[key] = comp

        return result or None

    def parse_coordinates(
        self, row: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        if not row:
            return None
        text = clean_infobox_text(row.get("text")) or ""
        return self._parse_position(text)

    @staticmethod
    def _parse_position(text: str) -> Optional[Dict[str, float]]:
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

    @staticmethod
    def _parse_area(self, row: Optional[Dict[str, Any]]) -> Optional[Dict[str, float]]:
        """Area: np. '277 acres (112 ha)' -> acres + hectares."""
        if not row:
            return None
        text = clean_infobox_text(row.get("text")) or ""
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
